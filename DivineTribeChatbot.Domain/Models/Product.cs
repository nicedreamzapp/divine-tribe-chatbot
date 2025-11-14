namespace DivineTribeChatbot.Domain.Models;

public class Product
{
    public string Id { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public string FullName { get; set; } = string.Empty;
    public string Url { get; set; } = string.Empty;
    public string Price { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public int Priority { get; set; }
    public double SearchBoost { get; set; } = 1.0;
    public bool InStock { get; set; } = true;
    public string Description { get; set; } = string.Empty;
    public List<string> Images { get; set; } = new();
    public string Sku { get; set; } = string.Empty;
    public List<string> Features { get; set; } = new();
    public List<string> Keywords { get; set; } = new();
    public Dictionary<string, string> Metadata { get; set; } = new();
}
