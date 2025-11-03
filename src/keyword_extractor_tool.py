import re
from research_tool import Research_Tool
from typing import List, Set
from collections import Counter
from fairlib import AbstractTool



class Keyword_Extractor_Tool(AbstractTool):
    name = "keyword_extractor_tool"
    description = (
        "Extracts potential keywords from a body of text. Use this when ",
        "you are gathering ideas for potential topics to research. Be ",
        "advised that the keywords extracted by this tool may need to be ",
        "slightly adapted in order to better fit the context of the essay.",
        "This tool accepts a body of text as an input and returns a formatted ",
        "list of extracted keywords, which are suitable to be converted into ",
        "research topics."
    )
    
    def use(self, input_str : str):
        return find_topics(input_str)


def extract_topics_from_text(text: str, max_topics: int = 5) -> List[str]:
    """
    Extract key topics/keywords from input text.
    Uses word frequency and length heuristics to identify meaningful terms.
    
    Args:
        text: The input document text
        max_topics: Maximum number of topics to extract
        
    Returns:
        List of topic strings to research
    """
    # Convert to lowercase and extract words (5+ characters to be more selective)
    words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
    
    # Expanded stop words list - common words that don't make good search terms
    stop_words = {
        'that', 'this', 'with', 'have', 'from', 'they', 'been', 
        'were', 'will', 'their', 'what', 'about', 'which', 'when',
        'there', 'would', 'could', 'should', 'these', 'those', 'than',
        'where', 'while', 'being', 'other', 'often', 'through', 'between',
        'during', 'before', 'after', 'under', 'around', 'within', 'without',
        'highly', 'human', 'humans', 'known', 'called', 'named', 'various',
        'several', 'including', 'making', 'still', 'years', 'number',
        'people', 'things', 'place', 'found', 'however', 'among', 'another'
    }
    
    # Filter out stop words
    filtered_words = [w for w in words if w not in stop_words]
    
    # Count word frequency
    word_freq = Counter(filtered_words)
    
    # Get most common words as topics
    topics = [word for word, count in word_freq.most_common(max_topics)]
    
    return topics


def extract_phrases_from_text(text: str, max_phrases: int = 3) -> List[str]:
    """
    Extract multi-word phrases that might be important topics.
    Looks for capitalized phrases or quoted terms.
    
    Args:
        text: The input document text
        max_phrases: Maximum number of phrases to extract
        
    Returns:
        List of phrase strings to research
    """
    phrases = []
    
    # Find quoted phrases
    quoted = re.findall(r'"([^"]+)"', text)
    phrases.extend(quoted[:max_phrases])
    
    # Find capitalized multi-word terms (but not sentence starts)
    # This catches things like "Golden Retriever" or "Service Dogs"
    cap_phrases = re.findall(r'(?<=[.!?]\s)([A-Z][a-z]+(?: [A-Z][a-z]+)+)', text)
    phrases.extend(cap_phrases[:max_phrases - len(phrases)])
    
    return phrases[:max_phrases]


def deduplicate_sources(all_sources: List[str]) -> List[str]:
    """
    Remove duplicate URLs from collected sources.
    
    Args:
        all_sources: List of URLs (may contain duplicates)
        
    Returns:
        List of unique URLs
    """
    seen: Set[str] = set()
    unique = []
    
    for source in all_sources:
        if source not in seen:
            seen.add(source)
            unique.append(source)
    
    return unique


def find_topics(essay: str, interactive: bool = True):
    """
    Core agentic research function.
    
    Process:
    1. Extract topics and phrases from the essay
    2. Use Research_Tool to search for sources on each topic
    3. Collect and deduplicate all found sources
    4. Print summary of findings
    5. Optionally allow user to do additional searches
    
    Args:
        essay: The input text/document to research
        research_tool: Instance of Research_Tool for performing searches
        interactive: If True, prompts user for additional searches after completion
    """
    print("\n" + "="*60)
    print("[Keyword Extractor] Starting keyword extraction process...")
    print("="*60 + "\n")
    
    # Step 1: Extract topics from the essay
    print("[Keyword Extractor] 📝 Analyzing document for key topics...")
    
    single_word_topics = extract_topics_from_text(essay, max_topics=4)
    phrase_topics = extract_phrases_from_text(essay, max_phrases=2)
    
    all_topics = single_word_topics + phrase_topics
    
    print(f"[Keyword Extractor] ✓ Identified {len(all_topics)} topics to research:")
    for i, topic in enumerate(all_topics, 1):
        print(f"  {i}. '{topic}'")
        
    return all_topics
    
    # # Step 2: Research each topic
    # print(f"\n[Keyword Extractor] 🔍 Beginning research on {len(all_topics)} topics...\n")
    
    # all_sources = []
    # sources_by_topic = {}  # Track sources for each topic
    # successful_searches = 0
    
    # for idx, topic in enumerate(all_topics, 1):
    #     print(f"\n{'─'*60}")
    #     print(f"[Search {idx}/{len(all_topics)}] Researching: '{topic}'")
    #     print(f"{'─'*60}")
        
    #     try:
    #         result = research_tool.use(topic)
            
    #         # Handle different return formats
    #         sources = []
            
    #         if result:
    #             # If result is a dict with 'sources' key
    #             if isinstance(result, dict) and 'sources' in result:
    #                 sources = result['sources']
    #             # If result is a list directly
    #             elif isinstance(result, list):
    #                 sources = result
    #             # If result is a string (single URL)
    #             elif isinstance(result, str):
    #                 sources = [result]
            
    #         if sources:
    #             print(f"[Keyword Extractor] ✓ Found {len(sources)} sources for '{topic}'")
    #             all_sources.extend(sources)
    #             sources_by_topic[topic] = sources  # Store by topic
    #             successful_searches += 1
    #         else:
    #             print(f"[Keyword Extractor] ⚠ No sources returned for '{topic}'")
    #             print(f"[Keyword Extractor] Debug - Result type: {type(result)}, Value: {result}")
    #             sources_by_topic[topic] = []
                
    #     except Exception as e:
    #         print(f"[Keyword Extractor] ✗ Error researching '{topic}': {e}")
    #         sources_by_topic[topic] = []
    
    # # Step 3: Deduplicate and summarize
    # print(f"\n{'='*60}")
    # print("[Keyword Extractor] 📊 Research Summary")
    # print(f"{'='*60}")
    
    # unique_sources = deduplicate_sources(all_sources)
    
    # print(f"\n✓ Completed {successful_searches}/{len(all_topics)} successful searches")
    # print(f"✓ Total sources found: {len(all_sources)}")
    # print(f"✓ Unique sources: {len(unique_sources)}")
    
    # if sources_by_topic:
    #     print(f"\n📚 Sources by Topic:\n")
    #     for topic, sources in sources_by_topic.items():
    #         print(f"  [{topic.upper()}] - {len(sources)} sources")
    #         for i, source in enumerate(sources, 1):
    #             print(f"    {i}. {source}")
    #         print()  # Blank line between topics
    # else:
    #     print(f"\n⚠ No sources collected. Check if research_tool.use() is returning the links properly.")
    
    # print(f"\n{'='*60}")
    # print("[Keyword Extractor] ✅ Research process completed!")
    # print(f"{'='*60}\n")
    
    # # Interactive mode - allow additional research rounds
    # if interactive:
    #     already_searched = set(all_topics)
        
    #     while True:
    #         print("─" * 60)
    #         user_input = input("\n🔍 Search for more topics from the document? (press Enter to continue, 'q' to finish): ").strip().lower()
            
    #         if user_input == 'q':
    #             print("\n[Keyword Extractor] 👋 Ending research session.\n")
    #             break
            
    #         # Extract more topics, excluding ones already searched
    #         print("\n[Keyword Extractor] 📝 Extracting additional topics from document...")
    #         new_topics = extract_topics_from_text(essay, max_topics=8)
    #         new_topics = [t for t in new_topics if t not in already_searched][:3]  # Get 3 new topics
            
    #         if not new_topics:
    #             print("[Keyword Extractor] ⚠ No new topics found. All relevant keywords already searched!")
    #             continue
            
    #         print(f"[Keyword Extractor] ✓ Found {len(new_topics)} new topics: {new_topics}\n")
            
    #         # Search each new topic
    #         for idx, topic in enumerate(new_topics, 1):
    #             print(f"{'─'*60}")
    #             print(f"[Additional Search {idx}/{len(new_topics)}] Researching: '{topic}'")
    #             print(f"{'─'*60}")
                
    #             try:
    #                 result = research_tool.use(topic)
                    
    #                 sources = []
    #                 if result:
    #                     if isinstance(result, dict) and 'sources' in result:
    #                         sources = result['sources']
    #                     elif isinstance(result, list):
    #                         sources = result
    #                     elif isinstance(result, str):
    #                         sources = [result]
                    
    #                 if sources:
    #                     print(f"[Keyword Extractor] ✓ Found {len(sources)} sources for '{topic}'")
                        
    #                     # Add to our collections
    #                     all_sources.extend(sources)
    #                     sources_by_topic[topic] = sources
    #                     all_topics.append(topic)
    #                     already_searched.add(topic)
    #                     successful_searches += 1
    #                 else:
    #                     print(f"[Keyword Extractor] ⚠ No sources found for '{topic}'")
    #                     already_searched.add(topic)
                        
    #             except Exception as e:
    #                 print(f"[Keyword Extractor] ✗ Error researching '{topic}': {e}")
    #                 already_searched.add(topic)
        
    #     # Update final counts
    #     unique_sources = deduplicate_sources(all_sources)
    #     print(f"\n{'='*60}")
    #     print("[Keyword Extractor] 📊 Final Research Summary")
    #     print(f"{'='*60}")
    #     print(f"\n✓ Total topics researched: {len(all_topics)}")
    #     print(f"✓ Successful searches: {successful_searches}")
    #     print(f"✓ Total unique sources: {len(unique_sources)}\n")
    
    # return {
    #     'topics': all_topics,
    #     'sources': unique_sources,
    #     'sources_by_topic': sources_by_topic,  # Include categorized sources
    #     'total_searches': len(all_topics),
    #     'successful_searches': successful_searches
    # }