namespace DivineTribeChatbot.Domain.Models;

public class ChatResponse
{
    public string Response { get; set; } = string.Empty;
    public string Status { get; set; } = "success";
    public string SessionId { get; set; } = string.Empty;
    public List<Product>? ProductsShown { get; set; }
    public string? Intent { get; set; }
    public double? Confidence { get; set; }
}
