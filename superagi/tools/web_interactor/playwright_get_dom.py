from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field
from superagi.helper.browser_wrapper import browser_wrapper

from typing import Type, Optional, List

from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from sys import argv, exit, platform




black_listed_elements = set(["html", "head", "title", "meta", "iframe", "body", "style", "script", "path", "svg", "br", "::marker",])

class GetDOMSchema(BaseModel):
    url: str = Field(..., description="The URL of the page whose DOM needs to be extracted")


class GetDOMTool(BaseTool):
    name = "PlaywrightGetDOM"
    description = "A tool to retrieve the rendered DOM from the current page.Returns a simplified DOM of the current web page. The id is specific to this plugin and will be needed to interact with elements. Make sure to run this before interacting with any elements on a webpage. Re-run this each time you're on a new webpage and want to interact with elements"
    args_schema = GetDOMSchema

    def _execute(self) -> str:
        page = self.browser_wrapper.page
        page_element_buffer = self.browser_wrapper.page_element_buffer
        client = self.browser_wrapper.client

        if page is None:
            return "Error: Browser/Page has not been initialized yet. Please run Start Browser and Go to Page Tool first."

        self.print_page_information()
        percentage_progress_start, percentage_progress_end = self.calculate_progress()

        page_state_as_text = self.create_page_state_as_text(percentage_progress_start, percentage_progress_end)

        tree = self.capture_dom_snapshot()
        strings, document, nodes = self.extract_tree_components(tree)

        anchor_ancestry = {"-1": (False, None)}
        button_ancestry = {"-1": (False, None)}
        child_nodes = {}

        elements_in_view_port = self.gather_elements_in_view_port(nodes, strings, document, child_nodes, anchor_ancestry, button_ancestry)
    
        elements_of_interest = self.process_elements_of_interest(elements_in_view_port, child_nodes)
    
        if len(elements_of_interest) > 125:
            divided_elements_of_interest = self.divide_elements_of_interest(elements_of_interest)
            return repr(divided_elements_of_interest) + "This is not part of the DOM, note that not the entire DOM was returned as it exceeded the context limit. If you're sure what you need is not included in this DOM, you should find a workaround."

        return repr(elements_of_interest)


    def print_page_information(self):
        page = self.browser_wrapper.page
        page_element_buffer = self.browser_wrapper.page_element_buffer
        print("##################################     PAGE      ######################################")
        print(page)
        print("##################################     PAGE Buffer      ######################################")
        print(page_element_buffer)
        print("######################################     END    ##################################")


    def calculate_progress(self):
        page = self.browser_wrapper.page
        device_pixel_ratio = page.evaluate("window.devicePixelRatio")
        if platform == "darwin" and device_pixel_ratio == 1:  # lies
            device_pixel_ratio = 2

        win_scroll_x = page.evaluate("window.scrollX")
        win_scroll_y = page.evaluate("window.scrollY")
        win_upper_bound = page.evaluate("window.pageYOffset")
        win_left_bound = page.evaluate("window.pageXOffset")
        win_width = page.evaluate("window.screen.width")
        win_height = page.evaluate("window.screen.height")
        win_right_bound = win_left_bound + win_width
        win_lower_bound = win_upper_bound + win_height
        document_offset_height = page.evaluate("document.body.offsetHeight")
        document_scroll_height = page.evaluate("document.body.scrollHeight")

        percentage_progress_start = 1
        percentage_progress_end = 2

        return percentage_progress_start, percentage_progress_end


    def create_page_state_as_text(self, percentage_progress_start, percentage_progress_end):
        return [
            {
                "x": 0,
                "y": 0,
                "text": "[scrollbar {:0.2f}-{:0.2f}%]".format(
                    round(percentage_progress_start, 2), round(percentage_progress_end)
                ),
            }
        ]


    def capture_dom_snapshot(self):
        client = self.browser_wrapper.client
        return client.send(
            "DOMSnapshot.captureSnapshot",
            {"computedStyles": [], "includeDOMRects": True, "includePaintOrder": True},
        )


    def extract_tree_components(self, tree):
        strings = tree["strings"]
        document = tree["documents"][0]
        nodes = document["nodes"]
        return strings, document, nodes


    def gather_elements_in_view_port(self, nodes, strings, document, child_nodes, anchor_ancestry, button_ancestry):
        elements_in_view_port = []

        for index, node_name_index in enumerate(nodes["nodeName"]):
            node_parent = nodes["parentIndex"][index]
            node_name = strings[node_name_index].lower()

            is_ancestor_of_anchor, anchor_id = self.add_to_hash_tree(anchor_ancestry, "a", index, node_name, node_parent)
            is_ancestor_of_button, button_id = self.add_to_hash_tree(button_ancestry, "button", index, node_name, node_parent)

            try:
                cursor = document["layout"]["nodeIndex"].index(index)
            except:
                continue

            if node_name in black_listed_elements:
                continue

            [x, y, width, height] = document["layout"]["bounds"][cursor]
            x /= self.device_pixel_ratio
            y /= self.device_pixel_ratio
            width /= self.device_pixel_ratio
            height /= self.device_pixel_ratio

            elem_left_bound = x
            elem_top_bound = y
            elem_right_bound = x + width
            elem_lower_bound = y + height

            partially_is_in_viewport = (
                elem_left_bound < self.win_right_bound
                and elem_right_bound >= self.win_left_bound
                and elem_top_bound < self.win_lower_bound
                and elem_lower_bound >= self.win_upper_bound
            )

            if not partially_is_in_viewport:
                continue

            meta_data = []

            element_attributes = self.find_attributes(
                nodes["attributes"][index], ["type", "placeholder", "aria-label", "title", "alt"]
            )

            ancestor_exception = is_ancestor_of_anchor or is_ancestor_of_button
            ancestor_node_key = (
                None
                if not ancestor_exception
                else str(anchor_id)
                if is_ancestor_of_anchor
                else str(button_id)
            )
            ancestor_node = (
                None
                if not ancestor_exception
                else child_nodes.setdefault(str(ancestor_node_key), [])
            )

            if node_name == "#text" and ancestor_exception:
                text = strings[nodes["nodeValue"][index]]
                if text == "|" or text == "•":
                    continue
                ancestor_node.append({
                    "type": "type", "value": text
                })
            else:
                if (
                    node_name == "input" and element_attributes.get("type") == "submit"
                ) or node_name == "button":
                    node_name = "button"
                    element_attributes.pop("type", None)
            
                for key in element_attributes:
                    if ancestor_exception:
                        ancestor_node.append({
                            "type": "attribute",
                            "key":  key,
                            "value": element_attributes[key]
                        })
                    else:
                        meta_data.append(element_attributes[key])

            element_node_value = None

            if nodes["nodeValue"][index] >= 0:
                element_node_value = strings[nodes["nodeValue"][index]]
                if element_node_value == "|":
                    continue
            elif (
                node_name == "input"
                and index in nodes["inputValue"]["index"]
                and element_node_value is None
            ):
                node_input_text_index = nodes["inputValue"]["index"].index(index)
                text_index = nodes["inputValue"]["value"][node_input_text_index]
                if node_input_text_index >= 0 and text_index >= 0:
                    element_node_value = strings[text_index]

            if ancestor_exception and (node_name != "a" and node_name != "button"):
                continue

            elements_in_view_port.append(
                {
                    "node_index": str(index),
                    "backend_node_id": nodes["backendNodeId"][index],
                    "node_name": node_name,
                    "node_value": element_node_value,
                    "node_meta": meta_data,
                    "is_clickable": index in set(nodes["isClickable"]["index"]),
                    "origin_x": int(x),
                    "origin_y": int(y),
                    "center_x": int(x + (width / 2)),
                    "center_y": int(y + (height / 2)),
                }
            )

        return elements_in_view_port


    def process_elements_of_interest(self, elements_in_view_port, child_nodes):
        elements_of_interest = []
        id_counter = 0

        for element in elements_in_view_port:
            node_index = element.get("node_index")
            node_name = element.get("node_name")
            node_value = element.get("node_value")
            is_clickable = element.get("is_clickable")
            origin_x = element.get("origin_x")
            origin_y = element.get("origin_y")
            center_x = element.get("center_x")
            center_y = element.get("center_y")
            meta_data = element.get("node_meta")

            inner_text = f"{node_value} " if node_value else ""
            meta = ""

            if node_index in child_nodes:
                for child in child_nodes.get(node_index):
                    entry_type = child.get("type")
                    entry_value = child.get("value")

                    if entry_type == "attribute":
                        entry_key = child.get("key")
                        meta_data.append(f'{entry_key}="{entry_value}"')
                    else:
                        inner_text += f"{entry_value} "

            if meta_data:
                meta_string = " ".join(meta_data)
                meta = f" {meta_string}"

            if inner_text != "":
                inner_text = f"{inner_text.strip()}"

            converted_node_name = self.convert_name(node_name, is_clickable)

            if (
                (converted_node_name != "button" or meta == "")
                and converted_node_name != "link"
                and converted_node_name != "input"
                and converted_node_name != "img"
                and converted_node_name != "textarea"
            ) and inner_text.strip() == "":
                continue

            self.page_element_buffer[id_counter] = element

            if inner_text != "":
                elements_of_interest.append(
                    f"<{converted_node_name} id={id_counter}{meta}>{inner_text}</{converted_node_name}>"
                )
            else:
                elements_of_interest.append(
                    f"<{converted_node_name} id={id_counter}{meta}/>"
                )
            id_counter += 1

        return elements_of_interest


    def divide_elements_of_interest(self, elements_of_interest):
        id_counter = 0
        divided_elements_of_interest = []

        while id_counter <= 125:
            divided_elements_of_interest.append(elements_of_interest[id_counter])
            id_counter += 1

        return divided_elements_of_interest
