# AllEvents.in Event Scraper

Extract event data from AllEvents.in - concerts, festivals, sports, theater, and more. Fast, reliable, and easy to use.

## Features

✅ **Comprehensive Event Data** - Extract titles, dates, locations, prices, categories, images, and organizer details  
✅ **Smart Filtering** - Search by city and category  
✅ **Flexible Limits** - Control how many events to scrape  
✅ **Proxy Support** - Built-in Apify proxy integration  
✅ **AI-Ready Output** - Clean, structured JSON perfect for analysis

## Input Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `city` | String | Yes | City name (e.g., "washington", "new-york") |
| `category` | String | No | Event category (leave empty for all) |
| `maxResults` | Integer | No | Maximum events to scrape (default: 50) |
| `useProxy` | Boolean | No | Enable Apify proxy (default: false) |

## Output Fields

Each event contains:

- **title** - Event name
- **url** - Event page URL
- **date** - Event date
- **time** - Start time
- **location** - Venue/address
- **category** - Event type (music, sports, arts, etc.)
- **price** - Ticket price or "Free"
- **description** - Event details
- **image** - Poster image URL
- **organizer** - Organizer name
- **phone** - Contact phone
- **email** - Contact email

## Example Usage

### Basic Run
```json
{
  "city": "washington",
  "maxResults": 20
}
```

### Filter by Category
```json
{
  "city": "new-york",
  "category": "music",
  "maxResults": 50,
  "useProxy": true
}
```

## Sample Output

```json
{
  "title": "Summer Music Festival 2026",
  "url": "https://allevents.in/washington/summer-music-festival",
  "date": "2026-07-15",
  "time": "18:00",
  "location": "Central Park, New York",
  "category": "Music",
  "price": "$45",
  "description": "Join us for an amazing outdoor concert...",
  "image": "https://cdn.allevents.in/events/poster.jpg",
  "organizer": "NYC Events Inc",
  "phone": "+1-555-0123",
  "email": "info@nycevents.com"
}
```

## Use Cases

🎭 **Event Aggregation** - Build event listing websites  
📊 **Market Research** - Analyze event trends and pricing  
🤖 **AI Applications** - Train recommendation systems  
📱 **Mobile Apps** - Power event discovery apps  
🎫 **Ticket Platforms** - Source event inventory

## Pricing

💰 **Per-result**: $0.005 per event  
💰 **Per-run**: $0.05 per run

## Compatible with AI Agents

✅ Works seamlessly with **Claude**, **ChatGPT**, and other AI agents via [Apify MCP](https://apify.com/mcp)

## Support

Need help? Contact the developer or check the [Apify documentation](https://docs.apify.com).

---

**Built with ❤️ using Playwright and Apify SDK**
