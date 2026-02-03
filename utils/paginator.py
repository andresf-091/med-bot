TELEGRAM_MESSAGE_LIMIT = 1024


def split_content(content, limit=TELEGRAM_MESSAGE_LIMIT):
    if len(content) <= limit:
        return [content]

    pages = []
    paragraphs = content.split("\n\n")
    current_page = ""

    for para in paragraphs:
        if current_page and len(current_page) + len(para) + 2 > limit:
            pages.append(current_page.strip())
            current_page = para
        else:
            current_page = current_page + "\n\n" + para if current_page else para

    if current_page.strip():
        pages.append(current_page.strip())

    return pages
