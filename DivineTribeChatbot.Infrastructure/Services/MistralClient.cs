using System.Text;
using System.Text.Json;
using DivineTribeChatbot.Application.Interfaces;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace DivineTribeChatbot.Infrastructure.Services;

public class MistralClient : IMistralClient
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<MistralClient> _logger;
    private readonly string _apiKey;
    private readonly string _model;

    public MistralClient(
        HttpClient httpClient,
        IConfiguration configuration,
        ILogger<MistralClient> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        _apiKey = configuration["Mistral:ApiKey"] ?? throw new InvalidOperationException("Mistral API key not configured");
        _model = configuration["Mistral:Model"] ?? "mistral-medium-latest";

        _httpClient.BaseAddress = new Uri("https://api.mistral.ai/v1/");
        _httpClient.DefaultRequestHeaders.Add("Authorization", $"Bearer {_apiKey}");
    }

    public async Task<string> GenerateResponseAsync(string systemPrompt, string userPrompt)
    {
        try
        {
            var requestBody = new
            {
                model = _model,
                messages = new[]
                {
                    new { role = "system", content = systemPrompt },
                    new { role = "user", content = userPrompt }
                },
                temperature = 0.7,
                max_tokens = 500
            };

            var json = JsonSerializer.Serialize(requestBody);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            var response = await _httpClient.PostAsync("chat/completions", content);
            response.EnsureSuccessStatusCode();

            var responseJson = await response.Content.ReadAsStringAsync();
            var result = JsonSerializer.Deserialize<MistralResponse>(responseJson);

            var generatedText = result?.Choices?.FirstOrDefault()?.Message?.Content ?? string.Empty;

            _logger.LogInformation("Mistral API call successful. Response length: {Length}", generatedText.Length);

            return generatedText;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error calling Mistral API");
            return "I apologize, but I'm having trouble generating a response right now. Please try again.";
        }
    }

    private class MistralResponse
    {
        public List<Choice>? Choices { get; set; }
    }

    private class Choice
    {
        public Message? Message { get; set; }
    }

    private class Message
    {
        public string? Content { get; set; }
    }
}
