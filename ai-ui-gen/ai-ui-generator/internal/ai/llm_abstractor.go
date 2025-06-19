package ai

// LLMClient defines the interface for LLM communication
type LLMClient interface {
	Generate(prompt string) (string, error)
	StreamGenerate(prompt string, responseChannel chan string) error
}

// OpenAICompatibleClient implements LLMClient for OpenAI-compatible APIs
type OpenAICompatibleClient struct {
	endpoint    string
	apiKey      string
	modelName   string
	maxTokens   int
	temperature float64
}

// NewOpenAICompatibleClient creates a new OpenAI-compatible client
func NewOpenAICompatibleClient(endpoint, apiKey, modelName string, maxTokens int, temperature float64) *OpenAICompatibleClient {
	return &OpenAICompatibleClient{
		endpoint:    endpoint,
		apiKey:      apiKey,
		modelName:   modelName,
		maxTokens:   maxTokens,
		temperature: temperature,
	}
}

// Generate generates text using the LLM
func (c *OpenAICompatibleClient) Generate(prompt string) (string, error) {
	// TODO: Implement OpenAI-compatible API call
	// 1. Prepare request payload
	// 2. Make HTTP request
	// 3. Parse response
	return "", nil
}

// StreamGenerate generates text with streaming
func (c *OpenAICompatibleClient) StreamGenerate(prompt string, responseChannel chan string) error {
	// TODO: Implement streaming OpenAI-compatible API call
	// 1. Prepare streaming request
	// 2. Handle SSE responses
	// 3. Send chunks to channel
	return nil
}

// MockLLMClient implements LLMClient for testing
type MockLLMClient struct{}

// NewMockLLMClient creates a new mock LLM client
func NewMockLLMClient() *MockLLMClient {
	return &MockLLMClient{}
}

// Generate returns mock generated text
func (c *MockLLMClient) Generate(prompt string) (string, error) {
	return "// Mock generated code\nfunction MockComponent() {\n  return <div>Hello World</div>;\n}", nil
}

// StreamGenerate returns mock streaming text
func (c *MockLLMClient) StreamGenerate(prompt string, responseChannel chan string) error {
	mockResponse := "// Mock streaming response\nfunction Component() {\n  return <div>Streaming</div>;\n}"
	responseChannel <- mockResponse
	close(responseChannel)
	return nil
}
