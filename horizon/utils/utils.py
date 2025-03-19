import json
from django.utils.html import escape
from django.utils.safestring import mark_safe
import re


class HTMLConverter:
    """
    Converts structured content into formatted HTML.
    """

    def __init__(self):
        self.tag_patterns = {
            "p": re.compile(r'\{p (.*?) p\}', re.DOTALL),
            "hr": re.compile(r'\{hr hr\}', re.DOTALL),
            "img": re.compile(r'\{img (.*?) img\}', re.DOTALL),
            "a": re.compile(r'\{a (.*?) a\}', re.DOTALL),
            "b": re.compile(r'\{b (.*?) b\}', re.DOTALL),
            "h2": re.compile(r'\{h2 (.*?) h2\}', re.DOTALL),
            "h3": re.compile(r'\{h3 (.*?) h3\}', re.DOTALL),
            "figure_img": re.compile(r'\{figure_img (.*?) figure_img\}', re.DOTALL),
            "ads_by_google": re.compile(r'\{ads_by_google ads_by_google\}', re.DOTALL),
            "img_src_set": re.compile(r'\{img_src_set\}(.*?)\{img_src_set\}', re.DOTALL),
            "figure_img_src_set": re.compile(r'\{figure_img_src_set\}(.*?)\{figure_img_src_set\}', re.DOTALL),
            "ul": re.compile(r'\{ul(.*?)ul\}', re.DOTALL),
            "li": re.compile(r'\{li (.*?) li\}', re.DOTALL)
        }

    def get_html(self, document):
        for tag, pattern in self.tag_patterns.items():
            blocks = pattern.findall(document)
            document = self.replace_blocks(tag, blocks, document)

        return document
    
    def replace_blocks(self, tag, blocks, document):
        for block_content in blocks:
            if tag == "p":
                document = document.replace(f'{{p {block_content} p}}', f'<p class="text-[15px] sm:text-base md:text-lg text-gray-700 leading-relaxed pb-4">{block_content}</p>')
            if tag == "hr":
                document = document.replace(f'{{hr hr}}', f'<hr class="my-6 border-t-1 border-gray-300">')
            elif tag == "a":
                # {a click this link to buy on etsy blank href="https://etsy.com" target="_blank" a}
                # {a click this link to buy on etsy self href="https://etsy.com" target="_self" a}
                attributes, text = self.parse_a_attributes(block_content)
                document = document.replace(f'{{a {block_content} a}}', f'<a class="hover:text-accent text-[15px] sm:text-base md:text-lg underline" {attributes}>{text}</a>')
            elif tag == "b":
                document = document.replace(f'{{b {block_content} b}}', f'<strong>{block_content}</strong>')
            elif tag == "h2":
                document = document.replace(f'{{h2 {block_content} h2}}', f'<h2 class="text-xl sm:text-2xl md:text-3xl font-bold text-gray-800 leading-tight mt-4 mb-2">{block_content}</h2>')
            elif tag == "h3":
                document = document.replace(f'{{h3 {block_content} h3}}', f'<h3 class="text-base sm:text-lg md:text-xl font-bold text-gray-800 leading-tight mt-4 mb-2">{block_content}</h3>')
            elif tag == "img":
                # {img src="abc" alt="123" img}
                attributes = self.parse_img_attributes(block_content)
                document = document.replace(f'{{img {block_content} img}}', f'<img loading="lazy" {attributes}>')
            elif tag == "figure_img":
                # {figure_img src="abc" alt="123" figcaption="xyz" figure_img}
                attributes = self.parse_img_attributes(block_content)
                figure_caption = self.parse_figure_img_caption(block_content)

                document = document.replace(
                    f'{{figure_img {block_content} figure_img}}', 
                    f'''<figure class="w-full mx-auto text-center mb-8">
                        <img loading="lazy" {attributes} 
                            class="w-full h-auto object-cover shadow"
                        >
                        <figcaption class="text-gray-600 text-sm mt-2 italic">
                            {figure_caption}
                        </figcaption>
                    </figure>'''
                )
            elif tag == "ads_by_google":
                # {ads_by_google ads_by_google}
                document = document.replace(
                    f'{{ads_by_google ads_by_google}}', 
                    '''<div>
                        <ins class="adsbygoogle"
                            style="display:block; text-align:center;"
                            data-ad-layout="in-article"
                            data-ad-format="fluid"
                            data-ad-client="ca-pub-1785022650944518"
                            data-ad-slot="5657557332"></ins>
                            <script>
                                (adsbygoogle = window.adsbygoogle || []).push({});
                            </script>
                        </div>
                    '''
                )
            elif tag == "img_src_set":
                """
                {img_src_set}
                    src="some_image_url"
                    alt="some alt tag"
                    srcset="some_image_url_50 50w"
                    srcset="some_image_url_100 100w"
                    srcset="some_image_url_800 800w"
                {img_src_set}
                """
                attributes = self.parse_img_src_set_attributes(block_content)
                document = document.replace(f'{{img_src_set}}{block_content}{{img_src_set}}', f'<img loading="lazy" {attributes}>')
            elif tag == "figure_img_src_set":
                """
                {figure_img_src_set}
                    src="some_image_url"
                    figcaption="some caption"
                    alt="some alt tag"
                    srcset="some_image_url_50 50w"
                    srcset="some_image_url_100 100w"
                    srcset="some_image_url_800 800w"
                {figure_img_src_set}
                """
                attributes = self.parse_img_src_set_attributes(block_content)
                figure_caption = self.parse_figure_img_caption(block_content)
                document = document.replace(
                    f'{{figure_img_src_set}}{block_content}{{figure_img_src_set}}',
                    f'''<figure class="w-full mx-auto pb-4 text-center">
                        <img loading="lazy" {attributes} 
                            class="w-full h-auto object-cover mb-2 shadow"
                        >
                        <figcaption class="text-gray-600 text-sm italic">
                            {figure_caption}
                        </figcaption>
                    </figure>'''
                )
            elif tag == "ul":
                """
                {ul
                    {li some text li}
                    {li some text li}
                    {li some text li}
                ul}
                """
                # Process nested <li> elements inside {ul}
                li_matches = self.tag_patterns["li"].findall(block_content)
                li_html = "".join([f'<li class="ml-6 list-disc">{li}</li>' for li in li_matches])
                document = document.replace(f'{{ul{block_content}ul}}', f'<ul class="list-disc list-inside text-gray-800 space-y-2 mb-8">{li_html}</ul>')
            elif tag == "li":
                # Replace only standalone {li} tags (not needed since ul handles it)
                document = document.replace(f'{{li {block_content} li}}', f'<li class="ml-6 list-disc">{block_content}</li>')
            else:
                print(f"Unknown block type: {tag}")
        
        return document
    
    def parse_img_attributes(self, content):
        # Uses regex to extract src and alt attributes
        # Example: {img src="image.jpg" alt="An image" img}
        match = re.match(r'src="([^"]+)"\s+alt="([^"]+)"', content)
        if match:
            src, alt = match.groups()
            return f'src="{src}" alt="{alt}"'
        return ""
    

    def parse_figure_img_attributes(self, content):
        return self.parse_img_attributes(content)
    
    def parse_figure_img_caption(self, content):
        match = re.search(r'figcaption="([^"]+)"', content)
        if match:
            figcaption = match.group(1)  # Extract figcaption value
            return figcaption
        return ""
    
    def parse_a_attributes(self, content):
        # Uses regex to extract text, href, and target
        match = re.match(r'^(.*?)\s+href="([^"]+)"\s+target="([^"]+)"$', content)
        if match:
            text, href, target = match.groups()
            attributes = f'href="{href}" target="{target}"'
        else:
            text = content  # If no href or target is found, treat everything as text
            attributes = ""
        
        return attributes, text
    
    def parse_img_src_set_attributes(self, content):
        match = re.findall(r'([a-zA-Z-]+)="([^"]+)"', content)
        attributes = {}
        srcset_list = []
        
        for key, value in match:
            if key == "srcset":
                srcset_list.append(value)
            else:
                attributes[key] = value
        
        attributes_string = " ".join([f'{key}="{value}"' for key, value in attributes.items()])
        srcset_string = ", ".join(srcset_list)
        
        if srcset_string:
            attributes_string += f' srcset="{srcset_string}"'
        
        return attributes_string