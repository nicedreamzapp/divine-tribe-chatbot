namespace DivineTribeChatbot.Domain.Models;

public class ChatRequest
{
    public string Message { get; set; } = string.Empty;
    public string SessionId { get; set; } = string.Empty;
}
