import { DialogueData, DialogueState, DialogueEvent, Emotion } from './types';
import { ConversationRenderer } from './ConversationRenderer';
import { ChoicePresenter } from './ChoicePresenter';
import { EmotionSystem } from './EmotionSystem';
import { DialogueHistoryTracker } from './DialogueHistoryTracker';
import { InterruptionHandler } from './InterruptionHandler';
import { useInteractionState } from '../../store/core/interactionStore';
import { DialogueConfigPanel } from './DialogueConfigPanel';
import { DialogueConfigurationManager } from '../../dialogue/config/DialogueConfigurationManager';

export class DialogueManager {
  private container: HTMLElement;
  private state: DialogueState | null = null;
  private data: DialogueData | null = null;
  private isLoading: boolean = false;
  private unsubscribe: (() => void) | null = null;

  // Subcomponents
  private conversationRenderer!: ConversationRenderer;
  private choicePresenter!: ChoicePresenter;
  private emotionSystem!: EmotionSystem;
  private historyTracker!: DialogueHistoryTracker;
  private interruptionHandler!: InterruptionHandler;
  private configPanel: DialogueConfigPanel | null = null;
  private configPanelContainer: HTMLElement | null = null;
  private configPanelVisible: boolean = false;
  private configManager: DialogueConfigurationManager;

  constructor(containerId: string, configManager: DialogueConfigurationManager) {
    const element = document.getElementById(containerId);
    if (!element) {
      throw new Error(`Container element with id '${containerId}' not found`);
    }
    this.container = element;
    this.configManager = configManager;
    this.initializeUI();
    this.createConfigPanelToggle();
    // Store subscription must be set up externally via subscribeToStore
  }

  /**
   * Subscribe to store updates (call after instantiation)
   */
  public subscribeToStore(subscribeFn: (cb: (state: any) => void) => () => void) {
    this.unsubscribe = subscribeFn((state) => {
      if (state.lastDialogue) {
        this.showDialogue(state.lastDialogue);
      }
      this.setLoading(state.isLoading);
    });
  }

  /**
   * Unsubscribe from store updates (call on cleanup)
   */
  public unsubscribeFromStore() {
    if (this.unsubscribe) {
      this.unsubscribe();
      this.unsubscribe = null;
    }
  }

  /**
   * Show loading spinner or message
   */
  private setLoading(isLoading: boolean) {
    this.isLoading = isLoading;
    const loadingDiv = this.container.querySelector('#dialogue-loading') as HTMLElement;
    if (loadingDiv) {
      loadingDiv.style.display = isLoading ? 'block' : 'none';
    }
  }

  /**
   * Render dialogue from store update
   */
  private showDialogue(dialogue: any) {
    // Render dialogue message, participants, etc.
    const conversationDiv = this.container.querySelector('#dialogue-conversation') as HTMLElement;
    if (conversationDiv) {
      conversationDiv.innerText = dialogue.message;
      // Add cache status badge
      let badge = '';
      if (dialogue.cacheStatus === 'hit') {
        badge = ' (cached)';
      } else if (dialogue.cacheStatus === 'miss') {
        badge = ' (new)';
      }
      conversationDiv.innerText += badge;
      // Add GPT metadata
      if (dialogue.gptMetadata) {
        const meta = dialogue.gptMetadata;
        conversationDiv.innerText += `\nModel: ${meta.model}, Tokens: ${meta.tokensUsed}`;
      }
      // Add error message
      if (dialogue.error) {
        conversationDiv.innerText += `\n[Error: ${dialogue.error}]`;
      }
      // Add cache analytics
      if (dialogue.cacheAnalytics) {
        const analytics = dialogue.cacheAnalytics;
        conversationDiv.innerText += `\nCache hits: ${analytics.hits}, misses: ${analytics.misses}`;
      }
    }
    // Optionally update other UI elements (emotion, choices, etc.)
  }

  private initializeUI(): void {
    this.container.innerHTML = '';
    this.container.className = 'dialogue-ui';
    // Create subcomponent containers
    const conversationDiv = document.createElement('div');
    conversationDiv.id = 'dialogue-conversation';
    this.container.appendChild(conversationDiv);
    const choicesDiv = document.createElement('div');
    choicesDiv.id = 'dialogue-choices';
    this.container.appendChild(choicesDiv);
    const emotionDiv = document.createElement('div');
    emotionDiv.id = 'dialogue-emotion';
    this.container.appendChild(emotionDiv);
    const historyDiv = document.createElement('div');
    historyDiv.id = 'dialogue-history';
    this.container.appendChild(historyDiv);
    const interruptionDiv = document.createElement('div');
    interruptionDiv.id = 'dialogue-interruption';
    this.container.appendChild(interruptionDiv);
    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'dialogue-loading';
    loadingDiv.innerText = 'Loading...';
    loadingDiv.style.display = 'none';
    this.container.appendChild(loadingDiv);
    // Instantiate subcomponents
    this.conversationRenderer = new ConversationRenderer('dialogue-conversation');
    this.choicePresenter = new ChoicePresenter('dialogue-choices');
    this.emotionSystem = new EmotionSystem('dialogue-emotion');
    this.historyTracker = new DialogueHistoryTracker('dialogue-history');
    this.interruptionHandler = new InterruptionHandler('dialogue-interruption');
  }

  public startDialogue(data: DialogueData): void {
    this.data = data;
    this.state = {
      currentEventId: data.initialEventId,
      history: [],
      isActive: true,
    };
    this.renderCurrentEvent();
  }

  public advanceDialogue(choiceId?: string): void {
    if (!this.data || !this.state) return;
    const currentEvent = this.data.events.find(e => e.id === this.state!.currentEventId);
    if (!currentEvent) return;
    let nextEventId: string | undefined;
    if (choiceId) {
      const choice = currentEvent.choices.find(c => c.id === choiceId);
      nextEventId = choice?.nextEventId;
    } else if (currentEvent.choices.length === 1) {
      nextEventId = currentEvent.choices[0].nextEventId;
    }
    if (nextEventId) {
      this.state.currentEventId = nextEventId;
      this.state.history.push(currentEvent);
      this.renderCurrentEvent();
    } else {
      this.endDialogue();
    }
  }

  public endDialogue(): void {
    if (this.state) this.state.isActive = false;
    this.container.innerHTML = '';
  }

  private renderCurrentEvent(): void {
    if (!this.data || !this.state) return;
    const event = this.data.events.find(e => e.id === this.state!.currentEventId);
    if (!event) return;
    // Render conversation
    this.conversationRenderer.render(event);
    // Render emotion
    if (event.emotion) {
      this.emotionSystem.render(event.emotion);
    } else {
      this.emotionSystem.render(Emotion.Neutral);
    }
    // Render choices
    if (event.choices.length > 0) {
      this.choicePresenter.render(event.choices, (choiceId) => this.advanceDialogue(choiceId));
    } else {
      this.choicePresenter.render([], () => { });
    }
    // Render history
    this.historyTracker.render(this.state.history.concat([event]));
    // Handle interruptions
    if (event.type === 'interruption') {
      this.interruptionHandler.handleInterruption(event);
    } else {
      this.interruptionHandler.handleInterruption({ ...event, text: '' }); // Clear interruption
    }
  }

  /**
   * Creates a toggle button for the DialogueConfigPanel and mounts the panel container.
   */
  private createConfigPanelToggle(): void {
    // Create toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.textContent = '⚙️ Dialogue Config';
    toggleBtn.style.position = 'absolute';
    toggleBtn.style.top = '10px';
    toggleBtn.style.right = '10px';
    toggleBtn.onclick = () => this.toggleConfigPanel();
    this.container.appendChild(toggleBtn);
    // Create config panel container
    this.configPanelContainer = document.createElement('div');
    this.configPanelContainer.id = 'dialogue-config-panel-container';
    this.configPanelContainer.style.display = 'none';
    this.configPanelContainer.style.position = 'absolute';
    this.configPanelContainer.style.top = '50px';
    this.configPanelContainer.style.right = '10px';
    this.configPanelContainer.style.zIndex = '1001';
    this.container.appendChild(this.configPanelContainer);
    // Instantiate config panel
    this.configPanel = new DialogueConfigPanel('dialogue-config-panel-container', this.configManager);
  }

  /**
   * Toggles the visibility of the DialogueConfigPanel.
   */
  private toggleConfigPanel(): void {
    if (!this.configPanelContainer) return;
    this.configPanelVisible = !this.configPanelVisible;
    this.configPanelContainer.style.display = this.configPanelVisible ? 'block' : 'none';
  }
} 