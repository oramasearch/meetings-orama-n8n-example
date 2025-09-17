# Meetings Orama n8n Example

This repository demonstrates how to use n8n workflows with Orama Core to ingest and search meeting transcripts. The setup includes n8n for workflow automation and sample workflows, Orama Core for data search. There is also a simple sample dataset.

## Requirements

### System Requirements
- **Docker** and **Docker Compose** installed on your system
- **Git** for cloning the repository

### API Keys Required
You'll need the following API keys:
- **OpenAI API Key** - For LLM operations and embeddings
- **Hugging Face API Key** - For model downloads (if using local models)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd meetings-orama-n8n-example
```

### 2. Environment Configuration
Create a `.env` file in the root directory with your API keys:

```bash
# Copy the example file
cp .env.example .env
```

Edit the `.env` file and add your API keys:
```env
OPENAI_API_KEY=
ORAMA_CORE_MASTER_API_KEY=my-master-api-key # used internally, can be anything
HF_TOKEN=
```

**Important**: Replace the placeholder values with your actual API keys.

### 3. Start the Services
Run the following command to start all services:

```bash
docker-compose up -d
```

This will start:
- **n8n** (workflow automation) on port 5678
- **Orama Core** (vector search engine) on port 8080
- **Python AI Server** (embeddings and LLM) on port 50051
- **Config Processor** (environment variable processing)

### 4. Access n8n Interface
Once the services are running, you can access the n8n interface at:

**http://localhost:5678**

## Workflow Usage

### Initialize Flow (Required First Step)
**⚠️ Important**: You must run the Initialize flow first before using any other workflows.

1. In the n8n interface, find and open the **"Initialize"** workflow
2. Click **"Execute Workflow"** to run it
3. This workflow will:
   - Create the meetings collection in Orama Core
   - Set up the necessary indexes

**Note**: Re-running the Initialize flow will wipe existing indexes and recreate them.

### Basic Meetings Flow 

#### Data Ingestion
The **"Basic Meetings"** workflow handles the ingestion of meeting data through a web-based form interface:

#### Form Submission Process
1. **Access the Form**: The workflow provides a web form accessible at the n8n webhook URL
2. **Upload CSV File**: Use the form to upload a CSV file containing meeting data
3. **Automatic Processing**: Once submitted, the workflow automatically:
   - Extracts and parses the CSV data
   - Processes meeting summaries and utterances
   - Generates embeddings for semantic search
   - Stores data in two specialized Orama Core indexes

#### Sample Data Files
The repository includes three sample CSV files in the `sample_dataset` directory for testing:
- `2_meetings.csv` - Contains only 2 meetings for rapid testing and development
- `meetings.csv` - Contains the complete sample dataset with many meetings 


**CSV File Structure:**
All sample files contain the following columns:
- `id` - Unique identifier
- `Item_UID` - Item unique identifier  
- `Meeting_UID` - Meeting unique identifier
- `Transcript` - Full meeting transcript text
- `Summary` - Meeting summary
- `Date` - Meeting date


#### Chat Agent

The **"Basic Meetings"** workflow includes a fully functional chat agent that handles information about meetings using two specialized indexes:

**Two Indexes Architecture:**
1. **`meetings-summaries`** index: Contains meeting summaries with fields:
   - `id`: Meeting unique identifier
   - `summary`: Meeting summary text
   - `date`: Meeting date
   - `meeting_item`: Item unique identifier

2. **`meetings-utterances`** index: Contains contextual meeting snippets with fields:
   - `id`: Unique snippet identifier (Meeting_UID-start-end)
   - `meeting_id`: Reference to the meeting
   - `snippet`: Contextual window of utterances (up to 4 utterances for context)
   - `start`/`end`: Position markers within the transcript

**Chat Agent Features:**
- **Dual Search Strategy**: Uses two specialized tools:
  - `meetings_search_tool`: Searches the summaries index for high-level meeting information
  - `meeting_utterance_search_tool`: Searches the utterances index for specific dialogue context
- **Hybrid Search**: Combines semantic meaning and keyword matching for optimal results
- **Contextual Responses**: Provides relevant meeting excerpts with proper citations
- **Memory Buffer**: Maintains conversation context using a sliding window memory

**How to Use:**
1. The chat agent is automatically available when the "Basic Meetings" workflow is active
2. Send natural language queries about meetings
3. The agent will:
   - First search meeting summaries to identify relevant meetings
   - Then search specific utterances for detailed context
   - Combine results to provide comprehensive answers

**Example Queries:**
- "What was discussed about fireworks in Long Beach city council?"
- "Find meetings where budget decisions were made"
- "Show me discussions about infrastructure projects"
- "What topics were covered in April 2014 meetings?"

**Technical Implementation:**
- Uses OpenAI GPT-4.1-mini for natural language processing
- Leverages Orama Core's hybrid search capabilities
- Processes utterances in contextual windows for better understanding
- Maintains conversation history for follow-up questions

### Sample Data
The repository includes sample meeting data in the `sample_dataset` directory:
- `meetings.csv` - Full dataset with meeting transcripts
- `2_meetings.csv` - Smaller subset for testing

The CSV files contain the following columns:
- `id` - Unique identifier
- `Item_UID` - Item unique identifier  
- `Meeting_UID` - Meeting unique identifier
- `Transcript` - Full meeting transcript text
- `Summary` - Meeting summary
- `Date` - Meeting date


## Troubleshooting

### Common Issues

1. **GPU Not Available**: Ensure NVIDIA drivers and Docker GPU support are properly installed
2. **API Key Errors**: Verify your API keys are correctly set in the `.env` file
3. **Port Conflicts**: Make sure ports 5678, 8080, and 50051 are available


### Restart Services
To restart all services:
```bash
docker-compose down
docker-compose up -d
```

## Data Flow

1. **Initialize**: Set up collection and indexes in Orama Core
2. **Ingest**: Process CSV files and create embeddings
3. **Chat**: Query the indexed data using semantic search
4. **Retrieve**: Get relevant meeting transcripts based on search queries

## Next Steps

After running the Initialize and Basic Meetings flows:
- Explore the n8n interface to understand the workflow structure
- Modify workflows to suit your specific use case
- Add additional data sources or processing steps
- Customize the search and retrieval logic

For more information about Orama Core, visit the [official documentation](https://docs.oramasearch.com/).
