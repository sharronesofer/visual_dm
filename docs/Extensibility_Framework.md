# VisualDM Extensibility Framework

This document describes the extensibility framework for the VisualDM application.

## Overview

The VisualDM extensibility framework allows developers to extend and enhance the functionality of the VisualDM application through plugins. The framework provides a structured way to:

1. Create and load plugins
2. Define and implement extension points
3. Register extensions with extension points
4. Interact with extensions through a central registry

## Key Components

### Plugin Manager

The `PluginManager` class is the central component of the extensibility framework. It manages the loading and initialization of plugins, and serves as a registry for extension points and extensions. It provides methods for:

- Loading plugins from assemblies
- Registering plugins manually
- Managing the lifecycle of plugins (initialization, shutdown)
- Registering and finding extension points

The `PluginManager` is implemented as a singleton to provide easy access from anywhere in the application.

### Plugins

Plugins are self-contained modules that can extend the functionality of the VisualDM application. A plugin is a class that implements the `IPlugin` interface, which requires:

- Metadata properties: ID, name, version, author, description
- Initialization and shutdown methods
- Method to register extension points with the plugin manager

Plugins can provide both extension points (places where other plugins can extend functionality) and extensions (implementations that extend functionality at existing extension points).

### Extension Points

Extension points define specific locations in the application where functionality can be extended. An extension point is a class that implements the `IExtensionPoint` interface or extends the `ExtensionPointBase<T>` class, which provides:

- Metadata properties: ID, category, name, plugin ID
- Methods to register and retrieve extensions
- Type safety through generic parameters

Extension points are created by plugins or the core application and registered with the plugin manager. Other plugins can then find these extension points and register extensions with them.

### Extensions

Extensions are implementations that extend functionality at specific extension points. An extension is a class that implements an interface defined by the extension point. The extension point defines the contract that extensions must follow.

## Usage

### Creating a Plugin

To create a plugin, create a class that implements the `IPlugin` interface:

```csharp
public class MyPlugin : IPlugin
{
    public string Id => "com.example.myplugin";
    public string Name => "My Plugin";
    public string Version => "1.0.0";
    public string Author => "John Doe";
    public string Description => "Example plugin for VisualDM";
    
    public void Initialize()
    {
        // Initialize plugin resources
    }
    
    public void Shutdown()
    {
        // Clean up plugin resources
    }
    
    public void RegisterExtensionPoints(PluginManager pluginManager)
    {
        // Register extension points provided by this plugin
        var myExtensionPoint = new MyExtensionPoint(
            "com.example.myextensionpoint",
            "My Extension Point",
            Id
        );
        pluginManager.RegisterExtensionPoint(myExtensionPoint);
        
        // Register extensions for other extension points
        var otherExtensionPoint = pluginManager.GetExtensionPoint<OtherExtensionPoint>("com.example.otherextensionpoint");
        if (otherExtensionPoint != null)
        {
            otherExtensionPoint.RegisterExtension(new MyExtension());
        }
    }
}
```

### Creating an Extension Point

To create an extension point, create a class that extends `ExtensionPointBase<T>` where `T` is the interface that extensions must implement:

```csharp
public class MyExtensionPoint : ExtensionPointBase<IMyExtension>
{
    public string CustomProperty { get; private set; }
    
    public MyExtensionPoint(string id, string name, string pluginId, string customProperty) 
        : base(id, "MyCategory", name, pluginId)
    {
        CustomProperty = customProperty;
    }
    
    public void ExecuteAllExtensions()
    {
        foreach (var extension in GetExtensions())
        {
            extension.DoSomething();
        }
    }
}

public interface IMyExtension
{
    void DoSomething();
}
```

### Implementing an Extension

To create an extension, implement the interface defined by the extension point:

```csharp
public class MyExtension : IMyExtension
{
    public void DoSomething()
    {
        Debug.Log("MyExtension is doing something");
    }
}
```

### Using the Plugin Manager

To use the plugin manager, access the singleton instance and register plugins and extension points:

```csharp
// Get the plugin manager instance
var pluginManager = PluginManager.Instance;

// Register a plugin
var myPlugin = new MyPlugin();
pluginManager.RegisterPlugin(myPlugin);

// Get an extension point
var myExtensionPoint = pluginManager.GetExtensionPoint<MyExtensionPoint>("com.example.myextensionpoint");
if (myExtensionPoint != null)
{
    // Use the extension point
    myExtensionPoint.ExecuteAllExtensions();
}
```

## Example Use Cases

### UI Extensions

The extensibility framework can be used to allow plugins to add UI elements to specific locations in the application. For example:

- Main menu extensions
- Context menu extensions
- Tool panel extensions
- Status bar extensions

### Data Providers

Plugins can provide additional data to the application through data provider extension points. For example:

- Character data providers
- Item data providers
- Location data providers
- Quest data providers

### Rendering Extensions

Plugins can extend the rendering capabilities of the application through rendering extension points. For example:

- Custom rendering effects
- Custom visualization modes
- Custom map overlays

### Behavior Extensions

Plugins can extend the behavior of the application through behavior extension points. For example:

- Custom AI behaviors
- Custom game mechanics
- Custom event handlers

## Best Practices

### Extension Point Design

When designing extension points, follow these best practices:

- Define clear contracts for extensions through interfaces
- Use descriptive names for extension points and their interfaces
- Document the expected behavior of extensions
- Provide base classes for common extension patterns
- Use categories to organize extension points

### Plugin Design

When designing plugins, follow these best practices:

- Keep plugins focused on a specific set of features
- Handle initialization and shutdown gracefully
- Check for extension point availability before registering extensions
- Provide clear metadata for better plugin management
- Document extension points and extensions

### Performance Considerations

To ensure good performance when using the extensibility framework:

- Avoid excessive use of extension points in performance-critical code paths
- Consider caching extension results for frequently used extension points
- Minimize the overhead of calling extensions by batching operations
- Use extension point filters to limit the number of extensions processed

## Conclusion

The VisualDM extensibility framework provides a flexible and powerful way to extend the functionality of the application through plugins. By following the patterns and best practices described in this document, developers can create plugins that seamlessly integrate with the application and provide new features and enhancements. 