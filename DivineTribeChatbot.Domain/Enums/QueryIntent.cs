namespace DivineTribeChatbot.Domain.Enums;

public enum QueryIntent
{
    Unknown,
    OffTopic,
    MaterialShopping,      // Shopping for concentrate/dry herb products
    ProductInfo,           // Asking about specific product details
    ProductComparison,     // Comparing multiple products
    Troubleshooting,       // Device issues, problems
    HowTo,                 // Instructions, usage guidance
    CustomerService,       // Returns, warranty, orders, shipping
    AccessoryShopping,     // Looking for accessories/replacement parts
    Reasoning              // General advice, recommendations
}
