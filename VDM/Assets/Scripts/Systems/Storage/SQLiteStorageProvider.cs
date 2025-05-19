using System;
using System.Data;
using System.Threading.Tasks;
using System.Collections.Concurrent;
using System.IO;
#if UNITY_EDITOR || UNITY_STANDALONE
using Mono.Data.Sqlite;
#else
using Microsoft.Data.Sqlite;
#endif

namespace VisualDM.Storage
{
    /// <summary>
    /// SQLite-based implementation of IStorageProvider for structured data storage.
    /// </summary>
    public class SQLiteStorageProvider : IStorageProvider
    {
        private readonly string _dbPath;
        private readonly string _connectionString;
        private readonly ConcurrentBag<IDbConnection> _pool = new ConcurrentBag<IDbConnection>();
        private const int PoolSize = 4;

        public SQLiteStorageProvider(string dbPath)
        {
            _dbPath = dbPath;
            _connectionString = $"Data Source={_dbPath};Version=3;Pooling=True;Max Pool Size={PoolSize};";
            EnsureDatabase();
        }

        private void EnsureDatabase()
        {
            if (!File.Exists(_dbPath))
            {
                using var conn = CreateConnection();
                conn.Open();
                using var cmd = conn.CreateCommand();
                cmd.CommandText = @"CREATE TABLE IF NOT EXISTS Storage (
                    Id TEXT PRIMARY KEY,
                    Data BLOB,
                    Version INTEGER,
                    Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                );";
                cmd.ExecuteNonQuery();
            }
        }

        private IDbConnection CreateConnection()
        {
#if UNITY_EDITOR || UNITY_STANDALONE
            return new SqliteConnection(_connectionString);
#else
            return new SqliteConnection(_connectionString);
#endif
        }

        private IDbConnection GetConnection()
        {
            if (_pool.TryTake(out var conn))
                return conn;
            return CreateConnection();
        }

        private void ReturnConnection(IDbConnection conn)
        {
            if (_pool.Count < PoolSize)
                _pool.Add(conn);
            else
                conn.Dispose();
        }

        public async Task<string> Save(string path, byte[] data, int version = 0)
        {
            return await Task.Run(() =>
            {
                using var conn = GetConnection();
                conn.Open();
                using var tx = conn.BeginTransaction();
                using var cmd = conn.CreateCommand();
                cmd.CommandText = @"INSERT OR REPLACE INTO Storage (Id, Data, Version) VALUES (@id, @data, @version);";
                var p1 = cmd.CreateParameter(); p1.ParameterName = "@id"; p1.Value = path;
                var p2 = cmd.CreateParameter(); p2.ParameterName = "@data"; p2.Value = data;
                var p3 = cmd.CreateParameter(); p3.ParameterName = "@version"; p3.Value = version;
                cmd.Parameters.Add(p1); cmd.Parameters.Add(p2); cmd.Parameters.Add(p3);
                cmd.ExecuteNonQuery();
                tx.Commit();
                ReturnConnection(conn);
                return path;
            });
        }

        public async Task<byte[]> Load(string path, int version = 0)
        {
            return await Task.Run(() =>
            {
                using var conn = GetConnection();
                conn.Open();
                using var cmd = conn.CreateCommand();
                cmd.CommandText = version > 0 ?
                    "SELECT Data FROM Storage WHERE Id = @id AND Version = @version" :
                    "SELECT Data FROM Storage WHERE Id = @id ORDER BY Version DESC LIMIT 1";
                var p1 = cmd.CreateParameter(); p1.ParameterName = "@id"; p1.Value = path;
                cmd.Parameters.Add(p1);
                if (version > 0)
                {
                    var p2 = cmd.CreateParameter(); p2.ParameterName = "@version"; p2.Value = version;
                    cmd.Parameters.Add(p2);
                }
                var result = cmd.ExecuteScalar();
                ReturnConnection(conn);
                if (result == null || result is DBNull) throw new StorageNotFoundException($"No data for {path} v{version}");
                return (byte[])result;
            });
        }

        public async Task<bool> Delete(string path)
        {
            return await Task.Run(() =>
            {
                using var conn = GetConnection();
                conn.Open();
                using var tx = conn.BeginTransaction();
                using var cmd = conn.CreateCommand();
                cmd.CommandText = "DELETE FROM Storage WHERE Id = @id";
                var p1 = cmd.CreateParameter(); p1.ParameterName = "@id"; p1.Value = path;
                cmd.Parameters.Add(p1);
                int rows = cmd.ExecuteNonQuery();
                tx.Commit();
                ReturnConnection(conn);
                return rows > 0;
            });
        }

        public async Task<bool> Exists(string path)
        {
            return await Task.Run(() =>
            {
                using var conn = GetConnection();
                conn.Open();
                using var cmd = conn.CreateCommand();
                cmd.CommandText = "SELECT 1 FROM Storage WHERE Id = @id LIMIT 1";
                var p1 = cmd.CreateParameter(); p1.ParameterName = "@id"; p1.Value = path;
                cmd.Parameters.Add(p1);
                var result = cmd.ExecuteScalar();
                ReturnConnection(conn);
                return result != null && !(result is DBNull);
            });
        }

        public async Task<string[]> List(string directory)
        {
            return await Task.Run(() =>
            {
                using var conn = GetConnection();
                conn.Open();
                using var cmd = conn.CreateCommand();
                cmd.CommandText = string.IsNullOrEmpty(directory)
                    ? "SELECT Id FROM Storage"
                    : "SELECT Id FROM Storage WHERE Id LIKE @dir";
                if (!string.IsNullOrEmpty(directory))
                {
                    var p1 = cmd.CreateParameter(); p1.ParameterName = "@dir"; p1.Value = directory + "%";
                    cmd.Parameters.Add(p1);
                }
                var ids = new System.Collections.Generic.List<string>();
                using var reader = cmd.ExecuteReader();
                while (reader.Read())
                    ids.Add(reader.GetString(0));
                ReturnConnection(conn);
                return ids.ToArray();
            });
        }

        public async Task<string> SaveStream(string path, Stream inputStream)
        {
            using var ms = new MemoryStream();
            await inputStream.CopyToAsync(ms);
            return await Save(path, ms.ToArray());
        }

        public async Task<Stream> LoadStream(string path)
        {
            var data = await Load(path);
            return new MemoryStream(data);
        }
    }
} 