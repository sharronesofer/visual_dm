using System;
using System.Text;
using System.Text.Json;

namespace Systems.Integration
{
    public interface ISerializationUtility
    {
        string Serialize<T>(T obj);
        T Deserialize<T>(string data);
    }

    public class JsonSerializationUtility : ISerializationUtility
    {
        public string Serialize<T>(T obj)
        {
            return JsonSerializer.Serialize(obj);
        }

        public T Deserialize<T>(string data)
        {
            return JsonSerializer.Deserialize<T>(data);
        }
    }
} 