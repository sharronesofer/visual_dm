using UnityEngine;
using VisualDM.UI.Search;
using System.Collections.Generic;

namespace VisualDM.UI.Search
{
    public class SearchUIManager : MonoBehaviour
    {
        private SearchInput searchInput;
        private FilterBuilder filterBuilder;
        private SearchResultsDisplay resultsDisplay;
        private EntityResultDisplay entityDisplay;

        void Start()
        {
            // Instantiate all components at runtime
            searchInput = CreateComponent<SearchInput>("SearchInput");
            filterBuilder = CreateComponent<FilterBuilder>("FilterBuilder");
            resultsDisplay = CreateComponent<SearchResultsDisplay>("ResultsDisplay");
            entityDisplay = CreateComponent<EntityResultDisplay>("EntityDisplay");

            // Layout
            searchInput.transform.position = new Vector3(100, 600, 0);
            filterBuilder.transform.position = new Vector3(100, 500, 0);
            resultsDisplay.transform.position = new Vector3(100, 100, 0);
            entityDisplay.transform.position = new Vector3(800, 100, 0);

            // Wire up events
            searchInput.OnSearchSubmitted += OnSearchSubmitted;
            searchInput.OnSuggestionSelected += OnSuggestionSelected;
            filterBuilder.OnFiltersChanged += OnFiltersChanged;
            resultsDisplay.OnPageChanged += OnPageChanged;
            resultsDisplay.OnSortChanged += OnSortChanged;
        }

        private T CreateComponent<T>(string name) where T : Component
        {
            var go = new GameObject(name);
            go.transform.SetParent(transform);
            return go.AddComponent<T>();
        }

        private void OnSearchSubmitted(string query)
        {
            // TODO: Call backend search API with query and filters
            // Update resultsDisplay with new results
        }

        private void OnSuggestionSelected(string suggestion)
        {
            // Optionally auto-submit search or update input
        }

        private void OnFiltersChanged(List<string> filters)
        {
            // TODO: Call backend search API with current query and filters
        }

        private void OnPageChanged(int newPage)
        {
            // TODO: Fetch next/prev page from backend
        }

        private void OnSortChanged(string sortField)
        {
            // TODO: Update search results with new sort order
        }
    }
} 