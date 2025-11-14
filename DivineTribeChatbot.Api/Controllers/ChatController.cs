using DivineTribeChatbot.Application.Services;
using DivineTribeChatbot.Domain.Models;
using Microsoft.AspNetCore.Mvc;
using Markdig;

namespace DivineTribeChatbot.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ChatController : ControllerBase
{
    private readonly ChatService _chatService;
    private readonly ILogger<ChatController> _logger;

    public ChatController(ChatService chatService, ILogger<ChatController> logger)
    {
        _chatService = chatService;
        _logger = logger;
    }

    [HttpPost]
    public async Task<ActionResult<ChatResponse>> Chat([FromBody] ChatRequest request)
    {
        try
        {
            if (string.IsNullOrWhiteSpace(request.Message))
            {
                return BadRequest(new { error = "Message is required" });
            }

            var response = await _chatService.ProcessMessageAsync(request);

            // Convert markdown to HTML for rich formatting
            response.Response = Markdown.ToHtml(response.Response);

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing chat message");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }

    [HttpPost("feedback")]
    public async Task<ActionResult> SubmitFeedback([FromBody] FeedbackRequest request)
    {
        try
        {
            await _chatService.RecordFeedbackAsync(
                request.SessionId,
                request.ExchangeIndex,
                request.Feedback);

            return Ok(new { message = "Feedback recorded successfully" });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error recording feedback");
            return StatusCode(500, new { error = "Internal server error" });
        }
    }

    [HttpGet("health")]
    public ActionResult<object> Health()
    {
        return Ok(new
        {
            status = "healthy",
            timestamp = DateTime.UtcNow,
            version = "1.0.0"
        });
    }
}

public class FeedbackRequest
{
    public string SessionId { get; set; } = string.Empty;
    public int ExchangeIndex { get; set; }
    public string Feedback { get; set; } = string.Empty;
}
