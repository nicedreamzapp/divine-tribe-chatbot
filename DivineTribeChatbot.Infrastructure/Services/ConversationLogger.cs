using System.Text.Json;
using System.Text.Json.Serialization;
using DivineTribeChatbot.Application.Interfaces;
using DivineTribeChatbot.Domain.Models;
using Microsoft.Extensions.Logging;

namespace DivineTribeChatbot.Infrastructure.Services;

public class ConversationLogger : IConversationLogger
{
    private readonly string _logDirectory;
    private readonly ILogger<ConversationLogger> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public ConversationLogger(ILogger<ConversationLogger> logger, string logDirectory = "conversation_logs")
    {
        _logDirectory = logDirectory;
        _logger = logger;

        _jsonOptions = new JsonSerializerOptions
        {
            WriteIndented = true,
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
        };

        Directory.CreateDirectory(_logDirectory);
        _logger.LogInformation("Conversation Logger initialized - saving to {LogDirectory}/", _logDirectory);
    }

    public async Task LogConversationAsync(
        string sessionId,
        string userQuery,
        string botResponse,
        List<Product> productsShown,
        string intent,
        double confidence,
        string? feedback = null)
    {
        var timestamp = DateTime.UtcNow;
        var chatId = $"{sessionId}_{timestamp:yyyyMMdd_HHmmss_ffffff}";

        var logEntry = new ConversationLogEntry
        {
            ChatId = chatId,
            SessionId = sessionId,
            Timestamp = timestamp,
            UserQuery = userQuery,
            BotResponse = botResponse,
            ProductsShown = productsShown.Select(p => p.Name).ToList(),
            ProductUrls = productsShown.Select(p => p.Url).ToList(),
            Intent = intent,
            Confidence = confidence,
            Feedback = feedback
        };

        var dateStr = timestamp.ToString("yyyy-MM-dd");
        var logFilePath = Path.Combine(_logDirectory, $"{dateStr}.json");

        // Use a semaphore or lock to prevent concurrent file access issues
        await WriteLogEntryAsync(logFilePath, logEntry);
    }

    private async Task WriteLogEntryAsync(string logFilePath, ConversationLogEntry logEntry)
    {
        List<ConversationLogEntry> logs;

        // Read existing logs if file exists
        if (File.Exists(logFilePath))
        {
            try
            {
                var json = await File.ReadAllTextAsync(logFilePath);
                logs = JsonSerializer.Deserialize<List<ConversationLogEntry>>(json, _jsonOptions)
                       ?? new List<ConversationLogEntry>();
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error reading log file {FilePath}", logFilePath);
                logs = new List<ConversationLogEntry>();
            }
        }
        else
        {
            logs = new List<ConversationLogEntry>();
        }

        // Append new log entry
        logs.Add(logEntry);

        // Write back to file
        try
        {
            var json = JsonSerializer.Serialize(logs, _jsonOptions);
            await File.WriteAllTextAsync(logFilePath, json);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error writing log file {FilePath}", logFilePath);
        }
    }

    public async Task<List<ConversationLogEntry>> GetLogsByDateAsync(string dateStr)
    {
        var logFilePath = Path.Combine(_logDirectory, $"{dateStr}.json");

        if (!File.Exists(logFilePath))
        {
            return new List<ConversationLogEntry>();
        }

        try
        {
            var json = await File.ReadAllTextAsync(logFilePath);
            return JsonSerializer.Deserialize<List<ConversationLogEntry>>(json, _jsonOptions)
                   ?? new List<ConversationLogEntry>();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error reading log file {FilePath}", logFilePath);
            return new List<ConversationLogEntry>();
        }
    }

    public async Task<List<ConversationLogEntry>> GetRecentLogsAsync(int days = 1)
    {
        var allLogs = new List<ConversationLogEntry>();
        var logFiles = Directory.GetFiles(_logDirectory, "*.json")
            .OrderBy(f => f)
            .TakeLast(days);

        foreach (var logFile in logFiles)
        {
            try
            {
                var json = await File.ReadAllTextAsync(logFile);
                var logs = JsonSerializer.Deserialize<List<ConversationLogEntry>>(json, _jsonOptions);
                if (logs != null)
                {
                    allLogs.AddRange(logs);
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error reading log file {FilePath}", logFile);
            }
        }

        return allLogs;
    }

    public class ConversationLogEntry
    {
        public string ChatId { get; set; } = string.Empty;
        public string SessionId { get; set; } = string.Empty;
        public DateTime Timestamp { get; set; }
        public string UserQuery { get; set; } = string.Empty;
        public string BotResponse { get; set; } = string.Empty;
        public List<string> ProductsShown { get; set; } = new();
        public List<string> ProductUrls { get; set; } = new();
        public string Intent { get; set; } = string.Empty;
        public double Confidence { get; set; }
        public string? Feedback { get; set; }
        public DateTime? FeedbackTimestamp { get; set; }
    }
}
