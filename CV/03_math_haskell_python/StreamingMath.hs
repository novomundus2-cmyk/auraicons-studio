-- ============================================================================
-- MODULE: StreamingMath.hs
-- PURPOSE: Mathematical & Algebraic Foundations of Distributed Data Streaming
-- AUTHOR: Data Platform & Deployment Engineering Portfolio
-- ============================================================================
-- Why Haskell for Big Data Mathematics?
-- Distributed engines like Apache Spark, Flink, and Kafka Streams are built on
-- Category Theory and Abstract Algebra:
--   1. Functor (fmap)       -> Spark .map() / .select()
--   2. Monad (>>=)          -> Spark .flatMap() / .explode()
--   3. Semigroup (<>)       -> Spark .reduceByKey() (Associativity!)
--   4. Monoid (mempty, <>)  -> Spark .aggregateByKey() (Associativity + Identity!)
-- ============================================================================

module StreamingMath where

import Data.List (foldl')
import qualified Data.Map.Strict as Map

-- ============================================================================
-- 1. ALGEBRAIC DATA TYPES FOR FINANCIAL STREAMING
-- ============================================================================

data Transaction = Transaction
  { txnId    :: String
  , userId   :: String
  , amount   :: Double
  , category :: String
  , epochSec :: Integer
  } deriving (Show, Eq)

-- ============================================================================
-- 2. PARALLEL WELFORD MONOID (Exact Distributed Mean, Variance & Z-Score)
-- ============================================================================
-- Naive variance E[X^2] - (E[X])^2 suffers from catastrophic cancellation
-- on large distributed datasets.
-- Chan-Golub-LeVeque / Welford's Parallel Monoid combines two partition states
-- A and B associatively in O(1) space and single pass:
--
--   n_AB  = n_A + n_B
--   delta = mu_B - mu_A
--   mu_AB = mu_A + delta * (n_B / n_AB)
--   M2_AB = M2_A + M2_B + delta^2 * (n_A * n_B / n_AB)
-- ============================================================================

data StatsMonoid = StatsMonoid
  { count :: !Int
  , mean  :: !Double
  , m2    :: !Double  -- Sum of squared differences from the mean
  } deriving (Show, Eq)

-- Singleton observation from a single transaction amount
singletonStats :: Double -> StatsMonoid
singletonStats x = StatsMonoid 1 x 0.0

instance Semigroup StatsMonoid where
  (StatsMonoid 0 _ _) <> b = b
  a <> (StatsMonoid 0 _ _) = a
  (StatsMonoid nA muA m2A) <> (StatsMonoid nB muB m2B) =
    let nAB   = nA + nB
        nA'   = fromIntegral nA
        nB'   = fromIntegral nB
        nAB'  = fromIntegral nAB
        delta = muB - muA
        muAB  = muA + delta * (nB' / nAB')
        m2AB  = m2A + m2B + (delta * delta) * (nA' * nB' / nAB')
    in StatsMonoid nAB muAB m2AB

instance Monoid StatsMonoid where
  mempty = StatsMonoid 0 0.0 0.0

-- Compute population variance: sigma^2 = M2 / N
variance :: StatsMonoid -> Double
variance (StatsMonoid n _ m2Val)
  | n <= 1    = 0.0
  | otherwise = m2Val / fromIntegral n

-- Compute standard deviation: sigma = sqrt(sigma^2)
stdDev :: StatsMonoid -> Double
stdDev = sqrt . variance

-- Compute anomaly Z-Score: z = |x - mu| / sigma
zScore :: StatsMonoid -> Double -> Double
zScore stats x =
  let s = stdDev stats
  in if s == 0.0 then 0.0 else abs (x - mean stats) / s

-- ============================================================================
-- 3. SHANNON INFORMATION ENTROPY (Traffic / Fraud Anomaly Detection)
-- ============================================================================
-- Formula: H(X) = - sum_{i} P(x_i) * log2(P(x_i))
-- High entropy -> Uniform distribution across categories/users (normal)
-- Sudden drop in entropy -> Concentration attack / Botnet / Skewed partition!
-- ============================================================================

shannonEntropy :: Ord a => [a] -> Double
shannonEntropy [] = 0.0
shannonEntropy xs =
  let total = fromIntegral (length xs) :: Double
      freqs = Map.elems $ foldl' (\acc x -> Map.insertWith (+) x (1 :: Int) acc) Map.empty xs
      probs = [ fromIntegral c / total | c <- freqs ]
  in negate $ sum [ p * logBase 2 p | p <- probs, p > 0 ]

-- ============================================================================
-- 4. QUEUEING THEORY & LITTLE'S LAW (Kafka Lag & NiFi Backpressure)
-- ============================================================================
-- Little's Law: L = lambda * W
--   L      = Average number of messages in queue (Consumer Lag / FlowFiles)
--   lambda = Arrival rate (messages / second)
--   W      = Average time a message spends in the system (latency in seconds)
--
-- Utilisation factor (M/M/c Queue): rho = lambda / (c * mu)
--   where c = number of partitions/executors, mu = service rate per executor.
--   CRITICAL INVARIANT: If rho >= 1.0, queue grows to infinity (OOM / Disk Full).
-- ============================================================================

littlesLawQueueSize :: Double -> Double -> Double
littlesLawQueueSize lambdaSec latencySec = lambdaSec * latencySec

clusterUtilization :: Double -> Int -> Double -> Double
clusterUtilization arrivalRate numExecutors serviceRatePerExecutor =
  arrivalRate / (fromIntegral numExecutors * serviceRatePerExecutor)

-- Minimum number of Spark Executors / Kafka Partitions needed to keep rho <= targetRho
minRequiredPartitions :: Double -> Double -> Double -> Int
minRequiredPartitions arrivalRate serviceRatePerExecutor targetRho =
  ceiling (arrivalRate / (serviceRatePerExecutor * targetRho))

-- ============================================================================
-- 5. SELF-VERIFICATION & CLASSROOM DEMO
-- ============================================================================

main :: IO ()
main = do
  putStrLn "============================================================"
  putStrLn " HASKELL STREAMING MATHEMATICS VERIFICATION"
  putStrLn "============================================================"

  -- Partition 1 and Partition 2 simulated on different Spark Executors
  let partition1 = map singletonStats [100.0, 120.0, 110.0, 130.0, 115.0]
  let partition2 = map singletonStats [95.0, 105.0, 125.0, 4500.0] -- 4500.0 is an outlier!

  -- Distributed reduction: fold each partition independently, then combine!
  let agg1 = mconcat partition1
  let agg2 = mconcat partition2
  let globalStats = agg1 <> agg2

  putStrLn $ "Global Count (N): " ++ show (count globalStats)
  putStrLn $ "Global Mean (mu): " ++ show (mean globalStats)
  putStrLn $ "Global StdDev (sigma): " ++ show (stdDev globalStats)
  putStrLn $ "Z-Score of €4500.0 txn: " ++ show (zScore globalStats 4500.0)

  let categories = ["groceries", "electronics", "fashion", "travel", "groceries", "luxury"]
  putStrLn $ "Shannon Entropy H(X) [bits]: " ++ show (shannonEntropy categories)

  let minParts = minRequiredPartitions 45000.0 6500.0 0.80
  putStrLn $ "Min partitions for 45,000 msg/s (at 6,500 msg/s/core, 80% load): " ++ show minParts
