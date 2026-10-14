from ddgs import DDGS


def web_search(query, max_results=5):

    try:

        results = DDGS().text(
            query,
            max_results=max_results
        )

        formatted_results = []

        for result in results:

            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")
            })

        return formatted_results

    except Exception as e:

        return [
            {
                "title": "Search Error",
                "url": "",
                "snippet": str(e)
            }
        ]