interface DramaFlowBridge {
  playVideo(id: number, url: string, title: string): void
  shareDrama?(id: number, title: string): void
  login?(token: string): void
  logout?(): void
}

interface Window {
  DramaFlowBridge?: DramaFlowBridge
}
