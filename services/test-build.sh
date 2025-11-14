#!/bin/bash

# Test Docker builds locally before pushing

set -e

echo "🔨 Testing Docker builds..."
echo ""

# Test Pub/Sub
echo "Building pubsub..."
docker build -t pubsub:test -f pubsub/Dockerfile .
echo "✅ Pub/Sub build successful"
echo ""

# Test Master Agent
echo "Building master-agent..."
docker build -t master-agent:test -f agents/master/Dockerfile .
echo "✅ Master Agent build successful"
echo ""

# Test Ingest Agent
echo "Building ingest-agent..."
docker build -t ingest-agent:test -f agents/ingest/Dockerfile .
echo "✅ Ingest Agent build successful"
echo ""

# Test Chat Agent
echo "Building chat-agent..."
docker build -t chat-agent:test -f agents/chat/Dockerfile .
echo "✅ Chat Agent build successful"
echo ""

echo "🎉 All builds successful!"
echo ""
echo "Clean up test images:"
echo "  docker rmi pubsub:test master-agent:test ingest-agent:test chat-agent:test"
