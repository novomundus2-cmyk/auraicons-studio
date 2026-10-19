export type IconCategory =
  | 'all'
  | 'navigation'
  | 'actions'
  | 'commerce'
  | 'media'
  | 'interface'
  | 'social'
  | 'tech';

export type IconStyleTheme =
  | 'glass'
  | 'neon'
  | 'minimal'
  | 'sunset'
  | 'duotone'
  | 'cyber'
  | 'emerald';

export type AnimationType =
  | 'bounce'
  | 'morph'
  | 'pulse'
  | 'glow'
  | 'spin'
  | 'tilt'
  | 'shake'
  | 'strokeDraw'
  | 'burst'
  | 'heartbeat';

export type TriggerMode = 'hover' | 'click' | 'loop' | 'magnetic';

export interface InteractiveIconDef {
  id: string;
  name: string;
  nameEs: string;
  category: IconCategory;
  tags: string[];
  description: string;
  defaultAnimation: AnimationType;
  // Morph alternate icon or state if applicable
  morphTarget?: string;
  badge?: string | number;
  // Specific SVG paths or instructions
  paths: {
    d: string;
    strokeWidth?: number;
    fill?: string;
    stroke?: string;
    strokeLinecap?: 'round' | 'inherit' | 'butt' | 'square';
    strokeLinejoin?: 'round' | 'inherit' | 'miter' | 'bevel';
    className?: string;
    style?: React.CSSProperties;
    animatedProps?: Record<string, unknown>;
  }[];
  customRender?: (props: IconRenderProps) => React.ReactNode;
}

export interface IconRenderProps {
  size: number;
  strokeWidth: number;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  isHovered: boolean;
  isActive: boolean;
  isToggled: boolean;
  theme: IconStyleTheme;
  animation: AnimationType;
  triggerMode: TriggerMode;
}

export interface StudioSettings {
  searchQuery: string;
  selectedCategory: IconCategory;
  selectedTheme: IconStyleTheme;
  strokeWidth: number;
  iconSize: number;
  primaryColor: string;
  secondaryColor: string;
  accentColor: string;
  animationSpeed: number; // 0.5 (fast) to 2 (slow)
  triggerMode: TriggerMode;
  enableMagnetic: boolean;
  enableSound: boolean;
  enableParticles: boolean;
  containerShape: 'none' | 'squircle' | 'circle' | 'square' | 'glass';
}
