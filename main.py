from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import BasicDetails  # Ensure BasicDetails.py is in the same directory or update the import path
import AboutReviews  # Import the AboutReviews module

app = FastAPI()

# Define a model for individual product details
class Product(BaseModel):
    asin: str
    name: str
    price: str
    ratings: str
    ratings_count: str
    link: str

# Define a response model that contains a list of products
class ScrapeResponse(BaseModel):
    status: str
    data: List[Product]

# Define a model for individual product reviews
class ProductReview(BaseModel):
    link: str
    review: str
    features: List[str]
    desc_title: List[str]
    desc_content: List[str]

# Define a response model that contains a list of product reviews
class ReviewResponse(BaseModel):
    status: str
    data: List[ProductReview]

# Define a request model for the input data
class ScrapeRequest(BaseModel):
    search_query: str
    num_pages: int
    dropdown_choice: int

@app.post("/scrape/basic/", response_model=ScrapeResponse)
async def scrape_amazon_products(request: ScrapeRequest) -> ScrapeResponse:
    try:
        # Call the scrape function from BasicDetails.py with the provided parameters
        data = BasicDetails.scrape_amazon_products(
            request.search_query, 
            request.num_pages, 
            request.dropdown_choice
        )
        
        # Assuming 'data' is a dictionary with lists for each field
        products = []
        for i in range(len(data['asin'])):
            product = Product(
                asin=data['asin'][i],
                name=data['name'][i],
                price=data['price'][i],
                ratings=data['ratings'][i],
                ratings_count=data['ratings_count'][i],
                link=data['link'][i],
            )
            products.append(product)
        
        return ScrapeResponse(status="success", data=products)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during scraping: {str(e)}")

@app.post("/scrape/reviews/", response_model=ReviewResponse)
async def scrape_amazon_reviews(request: ScrapeRequest) -> ReviewResponse:
    try:
        # Call the scrape function from AboutReviews.py with the provided parameters
        data = AboutReviews.scrape_amazon_details(
            request.search_query, 
            request.num_pages, 
            request.dropdown_choice
        )

        # Prepare a list of ProductReview objects
        reviews = []
        for i in range(len(data["product_links"])):
            product_review = ProductReview(
                link=data["product_links"][i],
                review=data["reviews"][i],
                features=data["features"][i],
                desc_title=data["desc_titles"][i],
                desc_content=data["desc_contents"][i],
            )
            reviews.append(product_review)

        return ReviewResponse(status="success", data=reviews)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during scraping: {str(e)}")

# Run the FastAPI app by saving this file and using the command:
# uvicorn test1:app --reload
