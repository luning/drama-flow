interface DramaFlowBridge {
  playVideo(episodeId: number, videoUrl: string, title: string, dramaId?: number, episodeNumber?: number): void
  openPlayer(episodeId: number, dramaId: number, episodeNumber: number): void
  shareDrama?(id: number, title: string): void
  login?(token: string): void
  logout?(): void
}

interface Window {
  DramaFlowBridge?: DramaFlowBridge
}
