from typing import Any



class DialogueManager {
  private container: HTMLElement
  private state: DialogueState | null = null
  private data: DialogueData | null = null
  private conversationRenderer!: ConversationRenderer
  private choicePresenter!: ChoicePresenter
  private emotionSystem!: EmotionSystem
  private historyTracker!: DialogueHistoryTracker
  private interruptionHandler!: InterruptionHandler
  constructor(containerId: str) {
    const element = document.getElementById(containerId)
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`)
    }
    this.container = element
    this.initializeUI()
  }
  private initializeUI(): void {
    this.container.innerHTML = ''
    this.container.className = 'dialogue-ui'
    const conversationDiv = document.createElement('div')
    conversationDiv.id = 'dialogue-conversation'
    this.container.appendChild(conversationDiv)
    const choicesDiv = document.createElement('div')
    choicesDiv.id = 'dialogue-choices'
    this.container.appendChild(choicesDiv)
    const emotionDiv = document.createElement('div')
    emotionDiv.id = 'dialogue-emotion'
    this.container.appendChild(emotionDiv)
    const historyDiv = document.createElement('div')
    historyDiv.id = 'dialogue-history'
    this.container.appendChild(historyDiv)
    const interruptionDiv = document.createElement('div')
    interruptionDiv.id = 'dialogue-interruption'
    this.container.appendChild(interruptionDiv)
    this.conversationRenderer = new ConversationRenderer('dialogue-conversation')
    this.choicePresenter = new ChoicePresenter('dialogue-choices')
    this.emotionSystem = new EmotionSystem('dialogue-emotion')
    this.historyTracker = new DialogueHistoryTracker('dialogue-history')
    this.interruptionHandler = new InterruptionHandler('dialogue-interruption')
  }
  public startDialogue(data: DialogueData): void {
    this.data = data
    this.state = {
      currentEventId: data.initialEventId,
      history: [],
      isActive: true,
    }
    this.renderCurrentEvent()
  }
  public advanceDialogue(choiceId?: str): void {
    if (!this.data || !this.state) return
    const currentEvent = this.data.events.find(e => e.id === this.state!.currentEventId)
    if (!currentEvent) return
    let nextEventId: str | undefined
    if (choiceId) {
      const choice = currentEvent.choices.find(c => c.id === choiceId)
      nextEventId = choice?.nextEventId
    } else if (currentEvent.choices.length === 1) {
      nextEventId = currentEvent.choices[0].nextEventId
    }
    if (nextEventId) {
      this.state.currentEventId = nextEventId
      this.state.history.push(currentEvent)
      this.renderCurrentEvent()
    } else {
      this.endDialogue()
    }
  }
  public endDialogue(): void {
    if (this.state) this.state.isActive = false
    this.container.innerHTML = ''
  }
  private renderCurrentEvent(): void {
    if (!this.data || !this.state) return
    const event = this.data.events.find(e => e.id === this.state!.currentEventId)
    if (!event) return
    this.conversationRenderer.render(event)
    if (event.emotion) {
      this.emotionSystem.render(event.emotion)
    } else {
      this.emotionSystem.render(Emotion.Neutral)
    }
    if (event.choices.length > 0) {
      this.choicePresenter.render(event.choices, (choiceId) => this.advanceDialogue(choiceId))
    } else {
      this.choicePresenter.render([], () => {})
    }
    this.historyTracker.render(this.state.history.concat([event]))
    if (event.type === 'interruption') {
      this.interruptionHandler.handleInterruption(event)
    } else {
      this.interruptionHandler.handleInterruption({ ...event, text: '' }) 
    }
  }
} 