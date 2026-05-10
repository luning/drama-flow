/**
 * DramaFlow Design System — TypeScript Tokens
 * 单一真相源（Single Source of Truth）
 *
 * 用法：React / Vue 组件中引用 tokens 对象，禁止硬编码色值。
 * CSS 变量版本见 tokens.css（保持同步）。
 * Figma 通过 Tokens Studio 插件与本文件双向同步。
 */

export const tokens = {
  color: {
    // 品牌色
    primary:      '#6C5CE7',
    primaryLight: '#A29BFE',
    accent:       '#FD79A8',

    // 品牌色 Alpha 变体
    primary90:      'rgba(108, 92, 231, 0.9)',
    primary85:      'rgba(108, 92, 231, 0.85)',
    primary80:      'rgba(108, 92, 231, 0.8)',
    primaryTint:    'rgba(108, 92, 231, 0.15)',
    primaryTintMd:  'rgba(108, 92, 231, 0.2)',

    // 语义色
    rating:  '#FFC048',
    success: '#00B894',
    danger:  '#E17055',
    info:    '#0984E3',
  },

  background: {
    outer:          '#1A1A2E',  // 手机壳外框
    primary:        '#0F0F23',  // 页面主背景
    card:           '#16163A',  // 卡片背景
    hover:          '#1C1C44',  // 悬停态
    elevated:       'rgba(20, 20, 50, 0.95)',  // 弹窗 / 毛玻璃
    skeleton:       '#1A1A3A',  // 骨架屏底色
    skeletonShine:  '#222244',  // 骨架屏高光
    deep:           '#2D1B4E',  // Banner 渐变深端
    cardDeep:       '#1A1A3E',  // 卡片渐变深端
    video:          '#000000',  // 视频播放器背景
  },

  border: {
    surfaceSubtle: 'rgba(255, 255, 255, 0.04)',
    subtle:        'rgba(255, 255, 255, 0.06)',
    default:       'rgba(255, 255, 255, 0.08)',
    surfaceMid:    'rgba(255, 255, 255, 0.10)',
    surfaceHover:  'rgba(255, 255, 255, 0.14)',
  },

  text: {
    primary:   '#FFFFFF',
    secondary: '#DDDDDD',
    label:     '#AAAAAA',  // 表单 label / 轻量描述
    tertiary:  '#888888',
    caption:   '#666666',  // 紧凑型元数据 / nav 未选中态
    muted:     '#555555',
    link:      '#A29BFE',
  },

  spacing: {
    xs:  '4px',
    sm:  '8px',
    md: '12px',
    lg: '16px',
    xl: '24px',
    '2xl': '32px',
    '3xl': '40px',
  },

  radius: {
    xs:   '4px',
    sm:   '6px',
    md:   '8px',
    btn: '12px',
    card:'14px',
    xl:  '20px',
    '2xl': '24px',
    full: '50%',
  },

  shadow: {
    sm:   '0 2px 8px rgba(0, 0, 0, 0.2)',
    md:   '0 4px 20px rgba(108, 92, 231, 0.3)',
    lg:   '0 8px 25px rgba(0, 0, 0, 0.3)',
    glow: '0 0 6px rgba(108, 92, 231, 0.5)',
  },

  transition: {
    fast:    '0.15s ease',
    default: '0.2s ease',
    page:    '0.35s cubic-bezier(0.4, 0, 0.2, 1)',
    banner:  '0.5s ease',
  },

  typography: {
    family: "-apple-system, 'Noto Sans SC', 'Roboto', sans-serif",
    size: {
      xs:    '10px',  // 角标 / 时长标签
      sm:    '12px',  // 辅助信息 / 元数据
      base:  '14px',  // 正文 / 卡片描述
      md:    '15px',  // 卡片标题 / 按钮文字
      lg:    '17px',  // Banner 标题 / App Bar
      xl:    '20px',  // 详情页标题
      '2xl': '24px',  // 大标题
      '3xl': '28px',  // 品牌名称
    },
    weight: {
      normal:    400,
      medium:    500,
      semibold:  600,
      bold:      700,
      extrabold: 800,
    },
  },
} as const

export type DesignTokens = typeof tokens
