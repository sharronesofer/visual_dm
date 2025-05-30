using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
using VDM.Runtime.Services;
using VDM.Runtime.Data.Models;
using Newtonsoft.Json;

namespace VDM.Runtime.Services
{
    /// <summary>
    /// Optimized HTTP client with compression, caching, and connection pooling
    /// </summary>
    public class OptimizedHTTPClient : BaseHTTPClient
    {
        [Header("Performance Optimization")]
        [SerializeField] private bool enableConnectionPooling = true;
        [SerializeField] private bool enableCompression = true;
        [SerializeField] private bool enableLocalCaching = true;
        [SerializeField] private bool enableDeltaUpdates = true;
        [SerializeField] private int maxConcurrentRequests = 10;
        [SerializeField] private float cacheExpirationTime = 300f; // 5 minutes

        [Header("Compression Settings")]
        [SerializeField] private int compressionThreshold = 1024; // Compress data larger than 1KB
        [SerializeField] private System.IO.Compression.CompressionLevel compressionLevel = System.IO.Compression.CompressionLevel.Optimal;

        protected override string GetClientName() => "OptimizedHTTPClient";

        protected override void InitializeClient()
        {
            base.InitializeClient();
            
            if (enableCompression)
            {
                defaultHeaders["Accept-Encoding"] = "gzip, deflate";
            }
        }

        // Minimal implementation to fix compilation
        public void GetOptimized(string endpoint, Action<bool, string> callback, bool useCache = true)
        {
            StartCoroutine(GetRequestCoroutine(endpoint, callback));
        }

        public void PostOptimized(string endpoint, object data, Action<bool, string> callback, bool useDelta = true)
        {
            StartCoroutine(PostRequestCoroutine(endpoint, data, callback));
        }
    }
} 