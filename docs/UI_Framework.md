# UI Framework Documentation

## Overview

The Visual DM UI Framework implements a Model-View-Controller (MVC) pattern to create maintainable, scalable user interfaces. The framework integrates with the existing Unity UI system and extends it with clear separation of concerns.

## Architecture

### Key Components

1. **UIModel**: Base class for all UI data models
   - Responsible for storing and managing data
   - Provides change notification through events
   - Encapsulates business logic related to data

2. **UIView**: Base class that inherits from PanelBase
   - Responsible for displaying the UI and capturing user input
   - Manages UI components, animations, and responsive layout
   - Communicates with its controller when input events occur

3. **UIController**: Base class for UI controllers
   - Mediates between model and view
   - Handles user input events from the view
   - Updates the model and/or view based on the application state
   - Manages the view lifecycle

4. **UIMVCManager**: Singleton manager for the MVC UI framework
   - Creates and manages the relationships between models, views, and controllers
   - Provides methods for showing/hiding UI elements
   - Implements a navigation stack for UI screens
   - Integrates with the existing UIManager

## Integration with Existing UI System

The UI framework leverages the existing `PanelBase` and `UIManager` classes:

- `UIView` inherits from `PanelBase` to utilize responsive layout and panel management
- `UIMVCManager` works alongside `UIManager` to handle dynamic UI creation and lifecycle

## Usage

### Basic Implementation Steps

1. **Create a Model Class**
   - Inherit from `UIModel`
   - Define properties and methods for your UI's data
   - Call `NotifyModelChanged()` when data changes

2. **Create a View Class**
   - Inherit from `UIView`
   - Define UI components and layout
   - Implement `UpdateView()` to reflect model changes
   - Define event handlers for user input

3. **Create a Controller Class**
   - Inherit from `UIController`
   - Subscribe to view events and model changes
   - Implement business logic for handling interactions

4. **Register and Use the UI**
   - Create your MVC components through `UIMVCManager`
   - Show/hide the UI using controller methods

### Example: Dialog UI

```csharp
// Model
public class DialogModel : UIModel 
{
    public string Title { get; private set; }
    public string Message { get; private set; }
    
    public void SetTitle(string title) 
    {
        Title = title;
        NotifyModelChanged();
    }
    
    public void SetMessage(string message) 
    {
        Message = message;
        NotifyModelChanged();
    }
}

// View
public class DialogView : UIView 
{
    private Text _titleText;
    private Text _messageText;
    private Button _okButton;
    
    public event Action OnOkClicked;
    
    public override void Initialize(UIController controller) 
    {
        base.Initialize(controller);
        SetupUI();
    }
    
    private void SetupUI() 
    {
        // Create UI components
        // ...
        
        _okButton.onClick.AddListener(() => OnOkClicked?.Invoke());
    }
    
    public override void UpdateView() 
    {
        var model = _controller.GetModel<DialogModel>();
        _titleText.text = model.Title;
        _messageText.text = model.Message;
    }
}

// Controller
public class DialogController : UIController 
{
    public DialogController(DialogModel model, DialogView view) : base(model, view) {}
    
    public override void Initialize() 
    {
        base.Initialize();
        
        // Subscribe to events
        GetView<DialogView>().OnOkClicked += OnOkButtonClicked;
        GetModel<DialogModel>().OnModelChanged += OnModelChanged;
    }
    
    private void OnOkButtonClicked() 
    {
        // Handle button click
        Hide();
    }
    
    private void OnModelChanged() 
    {
        GetView<DialogView>().UpdateView();
    }
}
```

### Usage in Game

```csharp
// Creating a dialog
var model = new DialogModel();
var view = UIMVCManager.Instance.CreateUIView<DialogView, DialogModel, DialogController>(
    model,
    "MyDialog",
    new Vector2(400, 300),
    Vector2.zero
);

// Getting the controller
var controller = UIMVCManager.Instance.GetController<DialogController>();

// Showing the dialog
controller.GetModel<DialogModel>().SetTitle("Hello");
controller.GetModel<DialogModel>().SetMessage("Welcome to Visual DM!");
controller.Show();
```

## Best Practices

1. **Keep Models Plain and Focused**
   - Models should only contain data and methods to manipulate that data
   - Avoid references to Unity components in models
   - Use properties with private setters and public getters

2. **Views Should Be Presentation-Only**
   - Views should not contain business logic
   - Views should communicate with controllers via events
   - Keep UI layout and visual aspects in the view

3. **Controllers Coordinate Everything**
   - Controllers should control the flow of data and interactions
   - Controllers should handle application logic
   - Keep references to other services/managers in controllers, not views

4. **Use Events for Communication**
   - Views should raise events for user interactions
   - Models should notify of data changes
   - Controllers should subscribe to both

5. **Proper Cleanup**
   - Always unsubscribe from events when disposing controllers
   - Remove UI event listeners in OnDisable or when the view is hidden

## Advanced Topics

### Animations

The framework supports show/hide animations:

```csharp
public override void AnimateShow() 
{
    transform.localScale = Vector3.zero;
    Show();
    StartCoroutine(AnimateScale(Vector3.zero, Vector3.one, 0.3f));
}

public override void AnimateHide(Action onComplete = null) 
{
    StartCoroutine(AnimateScale(Vector3.one, Vector3.zero, 0.3f, () => {
        Hide();
        onComplete?.Invoke();
    }));
}
```

### Responsive UI

Inherit the responsive behavior from PanelBase:

```csharp
public override void OnBreakpointChanged(UIManager.Breakpoint breakpoint) 
{
    switch(breakpoint) 
    {
        case UIManager.Breakpoint.Small:
            // Adjust for small screens
            break;
        case UIManager.Breakpoint.Medium:
            // Adjust for medium screens
            break;
        case UIManager.Breakpoint.Large:
            // Adjust for large screens
            break;
    }
}
```

### UI Navigation

UIMVCManager includes a navigation stack:

```csharp
// Show a UI and add it to navigation stack
UIMVCManager.Instance.ShowUI<SettingsController>(true);

// Go back to previous screen
UIMVCManager.Instance.NavigateBack();
```

## Example Implementation

See the `VisualDM.UI.Example` namespace for a complete example dialog implementation. 