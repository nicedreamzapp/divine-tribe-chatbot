namespace DivineTribeChatbot.Application.Interfaces;

public interface IMistralClient
{
    Task<string> GenerateResponseAsync(string systemPrompt, string userPrompt);
}
