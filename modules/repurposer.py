import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List

# Load environment variables from .env file
load_dotenv()

class Repurposer:
    """
    A class to handle AI-powered content repurposing using LangChain and Google Gemini.
    """
    def __init__(self):
        """
        Initializes the Repurposer with the Gemini model and defines various
        content repurposing chains.
        """
        # Ensure the Google API key is set as an environment variable
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set. "
                             "Please get your API key from Google AI Studio and set it.")
        
        # Initialize the Google Gemini Flash model
        # gemini-2.0-flash is chosen for its balance of performance and cost-efficiency
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, google_api_key=google_api_key)

        # Define output parser for tweet generation
        class TweetOutput(BaseModel):
            tweets: List[str] = Field(description="List of concise tweets, each under 280 characters.")

        self.tweet_parser = PydanticOutputParser(pydantic_object=TweetOutput)

        # Define prompts and chains for different repurposing options

        # 1. Blog Post Chain
        self.blog_prompt = PromptTemplate(
            input_variables=["original_content", "target_audience", "tone", "length"],
            template="""You are an expert content writer. Your task is to transform the given original content into a blog post.

Original Content:
"{original_content}"

Target Audience: {target_audience}
Tone: {tone}
Desired Length: {length} words (approximate)

Please write a compelling and well-structured blog post based on the above. Ensure it flows naturally and engages the specified audience. Include an introduction, main body with relevant points, and a conclusion.
"""
        )
        self.blog_chain = LLMChain(llm=self.llm, prompt=self.blog_prompt, output_key="blog_post")

        # 2. Tweet Thread Chain
        self.tweet_prompt = PromptTemplate(
            input_variables=["original_content", "tone"],
            template="""You are a social media expert. Your task is to convert the following content into a thread of 3-5 concise tweets. Each tweet must be under 280 characters. Use relevant hashtags and emojis where appropriate to maximize engagement.

Original Content:
"{original_content}"

Tone: {tone}

{format_instructions}

Please provide the tweets in a numbered list format.
"""
        )
        self.tweet_chain = LLMChain(
            llm=self.llm,
            prompt=self.tweet_prompt.partial(format_instructions=self.tweet_parser.get_format_instructions()),
            output_key="tweet_thread"
        )

        # 3. Instagram Carousel Text Chain
        self.carousel_prompt = PromptTemplate(
            input_variables=["original_content", "tone", "num_slides"],
            template="""You are an Instagram content creator. Your task is to generate text for an Instagram carousel post based on the given content. The carousel should have {num_slides} slides.

For each slide, provide:
- A concise, engaging headline/title.
- 2-3 bullet points or short sentences summarizing a key idea.
- Relevant emojis.
- A call to action for the last slide.

Original Content:
"{original_content}"

Tone: {tone}

Please format the output clearly, indicating each slide.
Example format:
--- Slide 1 ---
Headline: [Headline]
- Point 1
- Point 2
✨ Emoji

--- Slide 2 ---
Headline: [Headline]
- Point 1
- Point 2
🚀 Emoji
...
"""
        )
        self.carousel_chain = LLMChain(llm=self.llm, prompt=self.carousel_prompt, output_key="carousel_text")

        # You can add more chains here for other repurposing options (e.g., LinkedIn post, Email newsletter)

    def repurpose_content(self, content: str, option: str, **kwargs) -> str:
        """
        Repurposes the given content based on the selected option.

        Args:
            content (str): The original content to repurpose.
            option (str): The repurposing option (e.g., "Blog Post", "Tweet Thread", "Instagram Carousel").
            **kwargs: Additional parameters specific to the repurposing option.

        Returns:
            str: The repurposed content.
        """
        if option == "Blog Post":
            target_audience = kwargs.get("target_audience", "general audience")
            tone = kwargs.get("tone", "informative")
            length = kwargs.get("length", 500)
            inputs = {
                "original_content": content,
                "target_audience": target_audience,
                "tone": tone,
                "length": length
            }
            response = self.blog_chain.invoke(inputs)
            return response["blog_post"]
        elif option == "Tweet Thread":
            tone = kwargs.get("tone", "engaging")
            inputs = {
                "original_content": content,
                "tone": tone
            }
            response = self.tweet_chain.invoke(inputs)
            # The output parser will return a dictionary, extract the list of tweets
            parsed_output = self.tweet_parser.parse(response["tweet_thread"])
            return "\n\n".join(parsed_output.tweets)
        elif option == "Instagram Carousel":
            tone = kwargs.get("tone", "visual and inspiring")
            num_slides = kwargs.get("num_slides", 5)
            inputs = {
                "original_content": content,
                "tone": tone,
                "num_slides": num_slides
            }
            response = self.carousel_chain.invoke(inputs)
            return response["carousel_text"]
        else:
            return "Invalid repurposing option selected."

if __name__ == "__main__":
    # Example usage for testing the repurposer logic directly
    repurposer = Repurposer()
    
    sample_content = """
    Artificial intelligence (AI) is rapidly transforming various industries, from healthcare to finance. Machine learning, a subset of AI, enables systems to learn from data and make predictions or decisions without explicit programming. Deep learning, a further subset, uses neural networks with multiple layers to process complex patterns. The ethical implications of AI, such as bias in algorithms and job displacement, are critical considerations as the technology advances. Responsible AI development is crucial to ensure that these powerful tools benefit humanity.
    """

    print("--- Generating Blog Post ---")
    blog_output = repurposer.repurpose_content(
        sample_content,
        "Blog Post",
        target_audience="tech enthusiasts",
        tone="professional",
        length=400
    )
    print(blog_output)
    print("\n" + "="*50 + "\n")

    print("--- Generating Tweet Thread ---")
    tweet_output = repurposer.repurpose_content(
        sample_content,
        "Tweet Thread",
        tone="informative and engaging"
    )
    print(tweet_output)
    print("\n" + "="*50 + "\n")

    print("--- Generating Instagram Carousel Text ---")
    carousel_output = repurposer.repurpose_content(
        sample_content,
        "Instagram Carousel",
        tone="inspiring",
        num_slides=4
    )
    print(carousel_output)
    print("\n" + "="*50 + "\n")
