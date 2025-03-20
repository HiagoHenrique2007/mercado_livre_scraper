from lxml import html
import requests

class Scraper:
  def __init__(self):
    self.session = requests.Session() # sessão para otimizar as conexões de rede
    self.home_page = 'https://www.mercadolivre.com.br/' # pagina root do mercado livre
    self.headers = {
      'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
      'Connection': 'keep-alive',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0'
    }
  
  def getTree(self, url: str): 
    '''
      obtem a arvore do html para fazer parsing
    '''
    try:
      response = self.session.get(url, headers=self.headers)
      if response.ok:
        print(f'Tree da url: {url} - obtido!')
        return html.fromstring(response.text)
      else:
        print(f'Erro ao fazer a requisição ou obter a arvore da url: {url} - request status code: {response.status_code}')
    
    except Exception as e:
      print(f'Erro ao fazer requisição na url: {url} - Excessao: {e}')

  def getProductImg(self, tree) -> list[str]:
    imgs_url = tree.xpath("//figure[ contains(@class, 'ui-pdp-gallery__figure') ]/img[ contains(@class, 'ui-pdp-image ') and contains(@class, 'ui-pdp-gallery__figure__image') and not(contains(@src, 'data:image/gif')) ]/@src")
    return imgs_url

  def getProductName(self, tree) -> str | None:
    product_name = tree.xpath("//h1[contains(@class, 'ui-pdp-title')]//text()")
    return product_name[0]

  def getPrice(self, tree = None, url: str | None = None) -> float | None:
    if url is not None and tree is None:
      tree = self.getTree(url)
      if tree is None:
        return None
      price = tree.xpath("//span[@data-testid='price-part']//meta[@itemprop='price']/@content")
      return float(price[0])

    else:
      price = tree.xpath("//span[@data-testid='price-part']//meta[@itemprop='price']/@content")
      return float(price[0])

  def getRating(self, tree = None, url: str = None) -> float | None:
    if url is not None and tree is None:
      tree = self.getTree(url)
      if tree is None:
        return None
      rating = tree.xpath("//div[@data-testid='rating-component']//p[contains(@class, 'ui-review-capability__rating__average ')]//text()")
      return float(rating[0])

    rating = tree.xpath("//div[@data-testid='rating-component']//p[contains(@class, 'ui-review-capability__rating__average ')]//text()")
    return float(rating[0])

  def scrapeProduct(self, url: str) -> dict | None:
    '''
      Raspa o produto da url passada como parametro,
      valida se os links das imagens, nome, preço, avaliação e descrição
      foram coletador e retorna um dicionario com os dados
    '''
    tree = self.getTree(url)
    if tree is None:
      print.ical(f'Tree da url: {url} - está vazia!')
      return None
    
    product_name = self.getProductName(tree)
    price = self.getPrice(tree)
    rating = self.getRating(tree)
    description = self.getProductDescription(tree)
    imgs_ulr = self.getProductImg(tree)

    if not product_name:
      print(f'Nome do produto: {url} - esta vazio!')
      return None
    
    elif not price:
      print(f'Preço do produto: {product_name} - esta vazio!')
      return None
    
    elif not rating:
      print(f'A avaliação do produto: {product_name} - esta vazia!')
      return None
    
    elif not description:
      print(f'A descrição do produto: {product_name} - esta vazia!')
      return None
    
    print(f'Dados do produto: {product_name} - obtidos!')
    return {
      'product_name': product_name,
      'price': price,
      'rating': rating,
      'imgs': imgs_ulr
    }

  def scrapeProducts(self, urls: list | tuple) -> list[dict] | None:
    products_data = [ self.scrapeProduct(url) for url in urls ]
    if products_data is None:
      print(f'Lista de dados de scrapeProductsList() esta vazia!')
      return None
    return products_data

