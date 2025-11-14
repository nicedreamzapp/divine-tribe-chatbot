using DivineTribeChatbot.Application.Interfaces;
using DivineTribeChatbot.Application.Services;
using DivineTribeChatbot.Infrastructure.Services;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Add CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Register HttpClient for Mistral API
builder.Services.AddHttpClient<IMistralClient, MistralClient>();

// Register application services
builder.Services.AddSingleton<IQueryPreprocessor, QueryPreprocessor>();
builder.Services.AddSingleton<ICagCache, CagCache>();
builder.Services.AddSingleton<IAgentRouter, AgentRouter>();
builder.Services.AddSingleton<IContextManager, ContextManager>();
builder.Services.AddSingleton<IConversationMemory, ConversationMemory>();
builder.Services.AddSingleton<IConversationLogger, ConversationLogger>();
builder.Services.AddSingleton<IVectorStore, VectorStore>();
builder.Services.AddSingleton<IRagRetriever, RagRetriever>();
builder.Services.AddSingleton<IProductDatabase, ProductDatabase>();

// Register main chat service
builder.Services.AddScoped<ChatService>();

// Configure logging
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.AddDebug();

var app = builder.Build();

// Configure the HTTP request pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors();

app.UseAuthorization();

app.MapControllers();

// Initialize services
using (var scope = app.Services.CreateScope())
{
    var logger = scope.ServiceProvider.GetRequiredService<ILogger<Program>>();

    try
    {
        logger.LogInformation("Initializing Divine Tribe Chatbot...");

        // Load CAG Cache
        var cagCache = scope.ServiceProvider.GetRequiredService<ICagCache>();
        cagCache.Load();

        // Load Product Database
        var productDatabase = scope.ServiceProvider.GetRequiredService<IProductDatabase>();
        await productDatabase.LoadProductsAsync();

        logger.LogInformation("Divine Tribe Chatbot initialized successfully!");
    }
    catch (Exception ex)
    {
        logger.LogError(ex, "Error initializing chatbot");
    }
}

logger.LogInformation("Starting Divine Tribe Chatbot API on http://localhost:5001");

app.Run("http://localhost:5001");
