"""
Example implementation of an e-commerce shopping assistant using Model Context Protocol (MCP).
"""

import asyncio
from typing import List, Dict, Any
from modl.mcp.mcp_context import MCPContext, Tool, RetrievedDocument
from modl.mcp.mcp_interpreter import MCPInterpreter


# Mock product database
PRODUCTS = [
    {
        "name": "Vessi Cityscape",
        "price": 135,
        "color": "Slate Grey",
        "features": ["Waterproof", "Lightweight", "Minimalist"],
        "image_url": "https://example.com/vessi-cityscape.jpg",
        "product_link": "https://example.com/vessi-cityscape"
    },
    {
        "name": "Allbirds Mizzle",
        "price": 145,
        "color": "Natural White",
        "features": ["Water-resistant", "Wool blend", "Sustainable"],
        "image_url": "https://example.com/allbirds-mizzle.jpg",
        "product_link": "https://example.com/allbirds-mizzle"
    }
]


async def search_products(query: str) -> List[Dict[str, Any]]:
    """Mock product search function."""
    # In a real implementation, this would query a product database
    return [p for p in PRODUCTS if any(term.lower() in p["name"].lower() for term in query.split())]


async def check_price(product_link: str) -> Dict[str, Any]:
    """Mock price checking function."""
    # In a real implementation, this would check current prices
    product = next((p for p in PRODUCTS if p["product_link"] == product_link), None)
    if not product:
        return {"error": "Product not found"}
    return {
        "current_price": product["price"],
        "on_sale": False,
        "original_price": product["price"]
    }


async def compare_style(image_url: str, past_purchases: List[str]) -> Dict[str, Any]:
    """Mock style comparison function."""
    # In a real implementation, this would use computer vision to compare styles
    return {
        "style_match_percentage": 85,
        "matching_elements": ["color_scheme", "minimalist_design"],
        "style_notes": "Matches user's preference for minimalist, neutral designs"
    }


async def main():
    # Initialize MCP interpreter
    interpreter = MCPInterpreter()
    
    # Register tools
    interpreter.register_tool("search_products", search_products)
    interpreter.register_tool("check_price", check_price)
    interpreter.register_tool("compare_style", compare_style)
    
    # Create initial context
    context = MCPContext(
        system_instruction="You are a fashion-savvy personal shopping assistant helping users find stylish products.",
        user_goal="Find stylish, waterproof sneakers under €150 for city use in neutral colors and minimalist design.",
        user_profile={
            "name": "Pranav",
            "style": ["minimalist", "neutral", "luxury-but-practical"],
            "past_purchases": ["Common Projects", "On Cloudnova", "Nike Air Max 1"]
        }
    )
    
    # Add tools to context
    context.tools = [
        Tool(
            name="search_products",
            description="Search for products matching the given query",
            args=["query"]
        ),
        Tool(
            name="check_price",
            description="Check current price and sale status of a product",
            args=["product_link"]
        ),
        Tool(
            name="compare_style",
            description="Compare product style with user's past purchases",
            args=["image_url", "past_purchases"]
        )
    ]
    
    # Example interaction
    print("Initial context:")
    print(context.to_prompt())
    print("\n" + "="*50 + "\n")
    
    # Simulate a product search
    search_results = await interpreter.execute_tool(
        "search_products",
        query="waterproof sneakers neutral minimalist"
    )
    
    # Add results to context
    context.add_retrieved_document(
        source="ProductCatalog",
        query="waterproof sneakers neutral minimalist",
        results=search_results
    )
    
    # Simulate LLM response with tool calls
    llm_response = """
    Based on your style preferences, I've found some great options:
    
    <tool>check_price</tool>{"product_link": "https://example.com/vessi-cityscape"}
    <tool>compare_style</tool>{"image_url": "https://example.com/vessi-cityscape.jpg", "past_purchases": ["Common Projects", "On Cloudnova", "Nike Air Max 1"]}
    
    The Vessi Cityscape looks perfect for your needs - it's waterproof, minimalist, and in a neutral color.
    """
    
    # Process the response
    result = await interpreter.process_llm_response(context, llm_response)
    
    print("Tool Results:")
    for tool_result in result["tool_results"]:
        print(f"\n{tool_result['tool']}:")
        print(tool_result)
    
    print("\n" + "="*50 + "\n")
    
    # Update context with the interaction
    interpreter.update_context_from_response(
        context,
        llm_response,
        result["tool_results"]
    )
    
    print("Updated context:")
    print(context.to_prompt())


if __name__ == "__main__":
    asyncio.run(main()) 