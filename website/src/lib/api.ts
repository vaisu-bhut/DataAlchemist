// API client for the Knowledge Engine

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export interface ChatResponse {
  response: string;
  confidence: number;
  sources: Array<{
    conversation_id: string;
    similarity: number;
  }>;
}

export interface IngestData {
  conversations: Array<{
    conversation_id: string;
    customer_id: string;
    agent_id: string;
    messages: Array<{
      role: string;
      content: string;
    }>;
  }>;
}

export interface ChatQuery {
  query: string;
  customer_id: string;
}

class APIClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async ingestConversations(data: IngestData): Promise<void> {
    const response = await fetch(`${this.baseUrl}/api/v1/ingest`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to ingest data: ${error}`);
    }
  }

  async chatQuery(query: ChatQuery): Promise<ChatResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(query),
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`Failed to get chat response: ${error}`);
    }

    return response.json();
  }

  async healthCheck(): Promise<{ status: string; service: string }> {
    const response = await fetch(`${this.baseUrl}/health`);
    
    if (!response.ok) {
      throw new Error('Health check failed');
    }

    return response.json();
  }
}

export const apiClient = new APIClient(API_BASE_URL);

// Sample data for demo
export const sampleIngestData: IngestData = {
  conversations: [
    {
      conversation_id: 'conv_001',
      customer_id: 'customer_123',
      agent_id: 'agent_456',
      messages: [
        {
          role: 'customer',
          content: 'I cannot log into my account. It says my password is incorrect.',
        },
        {
          role: 'agent',
          content: 'I can help you reset your password. Please click on the "Forgot Password" link on the login page and follow the instructions sent to your email.',
        },
        {
          role: 'customer',
          content: 'I did that but I did not receive any email.',
        },
        {
          role: 'agent',
          content: 'Let me check your email address on file. Can you confirm your email is [email]?',
        },
        {
          role: 'customer',
          content: 'Yes, that is correct.',
        },
        {
          role: 'agent',
          content: 'I have manually sent a password reset link to your email. Please check your spam folder as well. The link will expire in 24 hours.',
        },
        {
          role: 'customer',
          content: 'Got it! Thank you so much.',
        },
      ],
    },
    {
      conversation_id: 'conv_002',
      customer_id: 'customer_456',
      agent_id: 'agent_789',
      messages: [
        {
          role: 'customer',
          content: 'My payment was declined but I have sufficient funds in my account.',
        },
        {
          role: 'agent',
          content: 'I apologize for the inconvenience. This can happen due to several reasons. First, please verify that your card details are entered correctly, including the CVV and expiration date.',
        },
        {
          role: 'customer',
          content: 'I double-checked everything and it is all correct.',
        },
        {
          role: 'agent',
          content: 'In that case, your bank might be blocking the transaction. Please contact your bank to authorize payments to our service. You can also try using a different payment method.',
        },
        {
          role: 'customer',
          content: 'Okay, I will call my bank. Thanks!',
        },
      ],
    },
    {
      conversation_id: 'conv_003',
      customer_id: 'customer_789',
      agent_id: 'agent_456',
      messages: [
        {
          role: 'customer',
          content: 'How do I cancel my subscription?',
        },
        {
          role: 'agent',
          content: 'To cancel your subscription, go to Settings > Billing > Manage Subscription, then click "Cancel Subscription". You will retain access until the end of your current billing period.',
        },
        {
          role: 'customer',
          content: 'Will I get a refund for the remaining days?',
        },
        {
          role: 'agent',
          content: 'We do not provide prorated refunds, but you will have full access until your subscription expires. If you change your mind, you can reactivate anytime before the expiration date.',
        },
        {
          role: 'customer',
          content: 'Understood, thank you.',
        },
      ],
    },
  ],
};

export const sampleChatQuery: ChatQuery = {
  query: 'I cannot log into my account',
  customer_id: 'customer_123',
};
