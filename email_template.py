
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser


def generate_email_variants(founder_data):
    model = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key="GEMINI_API_KEY",temperature=0.7)
    parser = JsonOutputParser()

    prompt = PromptTemplate(
        template="""You are an expert email copywriter specializing in communications between founders and investors. Your goal is to generate compelling and informative emails that clearly articulate an investment opportunity based on provided details.

Please generate multiple email variants for an investment opportunity presentation to an investor, using the following founder and company details. Ensure each email adheres to standard professional email structure: a clear subject line, a formal greeting, a concise introduction or purpose, a detailed body, a clear call to action, and a professional closing. Maintain a business and professional tone in clear English.

Here are the details:
1. Founder Name: {founder_name}
2. What are you building? {what_building}
3. Do you have co-builders? {co_builders}
4. Best contact? {best_contact}
5. Show what you built? {product_link}
6. Professional presence? {professional_presence}
7. Which industry does your product come under? {industry}
8. Company Name: {company_name}
9. Best description: {description}
10. Sectors: {sectors}
11. Current traction: {traction}
12. Required funding: {required_funding}
13. Previous funding: {previous_funding}
14. Choose your target countries: {target_countries}
15. Product stage: {product_stage}

Generate the following email variants, each tailored to a specific approach:

1.  **Custom**: Craft an email with a personalized touch. Highlight unique aspects of the company and the founder's journey, aiming for a conversational yet professional tone that showcases both the company’s personality and its potential.

2.  **Business**: Develop a formal, business-focused email. Emphasize the company's current traction, market opportunity, and financial needs. Use professional, clear, and concise language to convey a strong business proposition, providing both a brief overview and more detailed information.

3.  **Personal**: Create an email that shares the founder’s personal journey and vision behind the company. The tone should be engaging and human, while maintaining professionalism. Focus on connecting with the investor on a personal level while clearly outlining the business opportunity.

4.  **Metrics**: Generate an email that focuses on data-driven achievements, key performance indicators (KPIs), and measurable successes. Highlight the company’s growth, traction, and financials in a structured and easily understandable format, providing both a detailed analysis and a concise summary.

5.  **Vision**: Develop an inspiring email that focuses on the long-term impact and the founder's vision for the future. Clearly communicate the transformative potential of the product and the company’s mission, explaining how the investor can contribute to shaping this future.

Please return the response strictly in JSON format, with each variant as a key and the corresponding subject and body under each key.

The JSON should adhere to the following structure:

```json

  "Custom": "subject": "Subject line for Custom email", "body": "Body of the Custom email",
  "Business": "subject": "Subject line for Business email", "body": "Body of the Business email",
  "Personal": "subject": "Subject line for Personal email", "body": "Body of the Personal email",
  "Metrics": "subject": "Subject line for Metrics email", "body": "Body of the Metrics email",
  "Vision": "subject": "Subject line for Vision email", "body": "Body of the Vision email
  ```
  """,
        input_variables=[
            "founder_name", "what_building", "co_builders", "best_contact", "product_link",
            "professional_presence", "industry", "company_name", "description",
            "sectors", "traction", "required_funding", "previous_funding", "target_countries", "product_stage"
        ]
    )

    chain = prompt | model | parser

    response = chain.invoke({
        "founder_name": founder_data.get("founder_name", ""),
        "what_building": founder_data.get("what_building", ""),
        "co_builders": founder_data.get("co_builders", ""),
        "best_contact": founder_data.get("best_contact", ""),
        "product_link": founder_data.get("product_link", ""),
        "professional_presence": founder_data.get("professional_presence", ""),
        "industry": founder_data.get("industry", ""),
        "company_name": founder_data.get("company_name", ""),
        "description": founder_data.get("description", ""),
        "sectors": founder_data.get("sectors", ""),
        "traction": founder_data.get("traction", ""),
        "required_funding": founder_data.get("required_funding", ""),
        "previous_funding": founder_data.get("previous_funding", ""),
        "target_countries": founder_data.get("target_countries", ""),
        "product_stage": founder_data.get("product_stage", ""),
    })

    return response
