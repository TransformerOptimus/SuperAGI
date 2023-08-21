<p align="center">
  <a href="https://superagi.com//#gh-light-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Logo-dark.svg" width="318px" alt="SuperAGI logo" />
  </a>
  <a href="https://superagi.com//#gh-dark-mode-only">
    <img src="https://superagi.com/wp-content/uploads/2023/05/Logo-light.svg" width="318px" alt="SuperAGI logo" />
  </a>
</p>

# SuperAGI SerpApi Search Toolkit

The SuperAGI [SerpApi](https://serpapi.com) Search Toolkit helps users perform a search and extract snippets and webpages. The supported search engines are:
- Google
- Bing
- Baidu
- Yahoo!
- DuckDuckGo
- Yandex
- Naver
- Yelp
- ... (Find more at https://serpapi.com/search-api)

## ⚙️ Installation

### 🛠 **Setting Up of SuperAGI**
Set up the SuperAGI by following the instructions given (https://github.com/TransformerOptimus/SuperAGI/blob/main/README.MD)

### 🔧 **Add SerpApi API Key in SuperAGI Dashboard**

Sign up for a free account at [SerpApi](https://serpapi.com).

Navigate to the [Dashboard](https://serpapi.com/dashboard) page and find "Your Private API Key".

Open up the SerpApi Search Toolkit page in SuperAGI's Dashboard and paste your Private API Key.

### ⚡ **Pick a search engine**

You can specify "Serpapi Engine" in the SerpApi Search Toolkit page. Typical values are: `google`, `bing`, `baidu`, `yahoo`, `duckduckgo`, `yandex`, ...

The default value is `google` if not set.

For the complete list of valid engine values, please visit [SerpApi Documentation](https://serpapi.com/search-api).

### 💾 Disable caching

Set "Serpapi No Cache" to `true` if you want to force SerpApi to fetch the results even if a cached version is already present. Defaulted to `false`.

## Running SuperAGI SerApi Tool

You can simply ask your agent about the latest information regarding anything and your agent will be able to browse the internet to get that information for you.
