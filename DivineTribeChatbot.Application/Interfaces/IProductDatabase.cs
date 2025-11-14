using DivineTribeChatbot.Domain.Models;

namespace DivineTribeChatbot.Application.Interfaces;

public interface IProductDatabase
{
    Task LoadProductsAsync();
    List<Product> Search(string query, int limit = 5);
    List<Product> GetCategoryProducts(string category);
    Product? GetProductByUrl(string url);
}
