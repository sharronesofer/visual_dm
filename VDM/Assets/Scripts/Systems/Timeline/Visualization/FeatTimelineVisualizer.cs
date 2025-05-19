using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using VisualDM.Timeline.Models;
using VisualDM.Timeline.Processing;
using TMPro;

namespace VisualDM.Timeline.Visualization
{
    public class FeatTimelineVisualizer : MonoBehaviour
    {
        public FeatDataProcessor DataProcessor;
        public float TimelineLength = 16f; // Unity units for levels 1-20
        public float TimelineY = 0f;
        public float NodeSpacing = 0.7f;
        public float NodeVerticalSpread = 2.5f;
        public float PanSpeed = 1.0f;
        public float ZoomSpeed = 2.0f;
        public float MinZoom = 0.5f;
        public float MaxZoom = 2.5f;

        private List<TimelineNode> _nodes = new List<TimelineNode>();
        private List<TimelineEdge> _edges = new List<TimelineEdge>();
        private TooltipPanel _tooltipPanel;
        private TimelineNode _selectedNode;
        private Camera _mainCamera;
        private Dictionary<int, List<TimelineNode>> _nodesByLevel = new Dictionary<int, List<TimelineNode>>();

        private void Start()
        {
            _mainCamera = Camera.main;
            CreateTooltipPanel();
            RenderTimeline();
        }

        private void CreateTooltipPanel()
        {
            var canvasGO = new GameObject("TooltipCanvas");
            var canvas = canvasGO.AddComponent<Canvas>();
            canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            canvasGO.AddComponent<CanvasScaler>();
            canvasGO.AddComponent<GraphicRaycaster>();
            _tooltipPanel = new GameObject("TooltipPanel").AddComponent<TooltipPanel>();
            _tooltipPanel.transform.SetParent(canvasGO.transform, false);
            _tooltipPanel.gameObject.SetActive(false);
        }

        private void RenderTimeline()
        {
            if (DataProcessor == null || !DataProcessor.IsLoaded) return;
            var feats = DataProcessor.DataSet.Feats;
            _nodes.Clear();
            _edges.Clear();
            _nodesByLevel.Clear();

            // Draw axis
            var axisGO = new GameObject("TimelineAxis");
            var axisLine = axisGO.AddComponent<LineRenderer>();
            axisLine.positionCount = 2;
            axisLine.SetPosition(0, new Vector3(0, TimelineY, 0));
            axisLine.SetPosition(1, new Vector3(TimelineLength, TimelineY, 0));
            axisLine.startWidth = 0.1f;
            axisLine.endWidth = 0.1f;
            axisLine.material = new Material(Shader.Find("Sprites/Default"));
            axisLine.startColor = Color.white;
            axisLine.endColor = Color.white;

            // Draw tick marks and level labels
            for (int lvl = 1; lvl <= 20; lvl++)
            {
                float x = (lvl - 1) * (TimelineLength / 19f);
                var tickGO = new GameObject($"Tick_{lvl}");
                var tickLine = tickGO.AddComponent<LineRenderer>();
                tickLine.positionCount = 2;
                tickLine.SetPosition(0, new Vector3(x, TimelineY - 0.2f, 0));
                tickLine.SetPosition(1, new Vector3(x, TimelineY + 0.2f, 0));
                tickLine.startWidth = 0.05f;
                tickLine.endWidth = 0.05f;
                tickLine.material = new Material(Shader.Find("Sprites/Default"));
                tickLine.startColor = Color.gray;
                tickLine.endColor = Color.gray;

                // Level label
                var labelGO = new GameObject($"Label_{lvl}");
                var text = labelGO.AddComponent<TextMeshPro>();
                text.text = lvl.ToString();
                text.fontSize = 2;
                text.color = Color.white;
                labelGO.transform.position = new Vector3(x, TimelineY - 0.5f, 0);
            }

            // Place nodes
            foreach (var feat in feats)
            {
                float x = (feat.LevelRequirement - 1) * (TimelineLength / 19f);
                float y = TimelineY + Random.Range(-NodeVerticalSpread, NodeVerticalSpread);
                var nodeGO = new GameObject($"Node_{feat.Id}");
                var node = nodeGO.AddComponent<TimelineNode>();
                node.Initialize(feat, GetColorByCategory(feat.Category));
                nodeGO.transform.position = new Vector3(x, y, 0);
                node.OnPointerEnter += HandleNodePointerEnter;
                node.OnPointerExit += HandleNodePointerExit;
                node.OnPointerClick += HandleNodePointerClick;
                _nodes.Add(node);
                if (!_nodesByLevel.ContainsKey(feat.LevelRequirement))
                    _nodesByLevel[feat.LevelRequirement] = new List<TimelineNode>();
                _nodesByLevel[feat.LevelRequirement].Add(node);
            }

            // Draw edges
            foreach (var node in _nodes)
            {
                foreach (var prereqId in node.FeatData.Prerequisites)
                {
                    var prereqNode = _nodes.FirstOrDefault(n => n.FeatData.Id == prereqId);
                    if (prereqNode != null)
                    {
                        var edgeGO = new GameObject($"Edge_{node.FeatData.Id}_to_{prereqId}");
                        var edge = edgeGO.AddComponent<TimelineEdge>();
                        edge.Initialize(prereqNode.transform.position, node.transform.position, Color.white);
                        _edges.Add(edge);
                    }
                }
            }

            // Progression gap/cluster indicators
            for (int lvl = 1; lvl <= 20; lvl++)
            {
                if (!_nodesByLevel.ContainsKey(lvl) || _nodesByLevel[lvl].Count == 0)
                {
                    // Gap: draw warning icon or marker
                    var gapGO = GameObject.CreatePrimitive(PrimitiveType.Quad);
                    gapGO.name = $"GapMarker_{lvl}";
                    gapGO.transform.position = new Vector3((lvl - 1) * (TimelineLength / 19f), TimelineY + 0.7f, 0);
                    gapGO.transform.localScale = new Vector3(0.2f, 0.2f, 0.2f);
                    var renderer = gapGO.GetComponent<Renderer>();
                    renderer.material.color = Color.red;
                }
                else if (_nodesByLevel[lvl].Count > 4)
                {
                    // Cluster: draw cluster marker
                    var clusterGO = GameObject.CreatePrimitive(PrimitiveType.Quad);
                    clusterGO.name = $"ClusterMarker_{lvl}";
                    clusterGO.transform.position = new Vector3((lvl - 1) * (TimelineLength / 19f), TimelineY + 1.0f, 0);
                    clusterGO.transform.localScale = new Vector3(0.2f, 0.2f, 0.2f);
                    var renderer = clusterGO.GetComponent<Renderer>();
                    renderer.material.color = Color.yellow;
                }
            }
        }

        private void HandleNodePointerEnter(TimelineNode node)
        {
            _tooltipPanel.SetText($"<b>{node.FeatData.Name}</b>\n{node.FeatData.Description}\n<color=grey>Level: {node.FeatData.LevelRequirement}</color>");
            _tooltipPanel.gameObject.SetActive(true);
        }

        private void HandleNodePointerExit(TimelineNode node)
        {
            _tooltipPanel.gameObject.SetActive(false);
        }

        private void HandleNodePointerClick(TimelineNode node)
        {
            if (_selectedNode != null)
                ClearHighlightPath(_selectedNode);
            _selectedNode = node;
            HighlightPrerequisitePath(node);
        }

        private void HighlightPrerequisitePath(TimelineNode node)
        {
            node.SetHighlight(true, Color.cyan);
            foreach (var prereqId in node.FeatData.Prerequisites)
            {
                var prereqNode = _nodes.FirstOrDefault(n => n.FeatData.Id == prereqId);
                if (prereqNode != null && !prereqNode.IsHighlighted)
                    HighlightPrerequisitePath(prereqNode);
            }
        }

        private void ClearHighlightPath(TimelineNode node)
        {
            node.SetHighlight(false);
            foreach (var prereqId in node.FeatData.Prerequisites)
            {
                var prereqNode = _nodes.FirstOrDefault(n => n.FeatData.Id == prereqId);
                if (prereqNode != null && prereqNode.IsHighlighted)
                    ClearHighlightPath(prereqNode);
            }
        }

        private void Update()
        {
            // Tooltip follow mouse
            if (_tooltipPanel != null && _tooltipPanel.gameObject.activeSelf)
            {
                Vector2 mousePos = Core.mousePosition;
                _tooltipPanel.SetPosition(mousePos + new Vector2(20, -20));
            }
            // Pan/zoom controls (mouse)
            if (Core.GetMouseButton(2))
            {
                float dx = -Core.GetAxis("Mouse X") * PanSpeed;
                float dy = -Core.GetAxis("Mouse Y") * PanSpeed;
                _mainCamera.transform.Translate(dx, dy, 0);
            }
            float scroll = Core.GetAxis("Mouse ScrollWheel");
            if (Mathf.Abs(scroll) > 0.01f)
            {
                float newSize = Mathf.Clamp(_mainCamera.orthographicSize - scroll * ZoomSpeed, MinZoom, MaxZoom);
                _mainCamera.orthographicSize = newSize;
            }
        }

        private Color GetColorByCategory(FeatCategory category)
        {
            switch (category)
            {
                case FeatCategory.Combat: return new Color(0.8f, 0.2f, 0.2f);
                case FeatCategory.Magic: return new Color(0.2f, 0.4f, 0.8f);
                case FeatCategory.Utility: return new Color(0.2f, 0.8f, 0.4f);
                case FeatCategory.Social: return new Color(0.8f, 0.6f, 0.2f);
                case FeatCategory.Exploration: return new Color(0.5f, 0.3f, 0.8f);
                default: return Color.gray;
            }
        }
    }
} 