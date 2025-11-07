``` mermaid
sequenceDiagram
    actor User
    participant LINE_Server
    
    box "Chat Friend Project"
        participant LineRouter
        participant LineWebhookHandler
        participant ConversationUsecase
        participant LinePlatformAdapter
    end

    User->>+LINE_Server: 1. Send Message
    
    LINE_Server->>+LineRouter: 2. Forward Webhook (HTTP POST)
    LineRouter->>+LineWebhookHandler: 3. Delegate Request
    
    Note over LineWebhookHandler: Verify Signature, Parse JSON
    
    LineWebhookHandler->>+ConversationUsecase: 4. execute(user_id, content)
    
    Note over ConversationUsecase: Business Logic (Manage conversation, call AI model, etc.)
    
    ConversationUsecase->>+LinePlatformAdapter: 5. send_message(user_id, message_object)
    
    Note over LinePlatformAdapter: Translate to LINE API Format
    
    LinePlatformAdapter->>+LINE_Server: 6. Send Reply (API Call)
    deactivate LinePlatformAdapter
    
    LINE_Server->>+User: 7. Deliver Reply
    deactivate LINE_Server
    
    deactivate ConversationUsecase
    deactivate LineWebhookHandler
    deactivate LineRouter

```