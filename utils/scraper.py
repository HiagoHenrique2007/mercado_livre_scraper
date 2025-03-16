from lxml import html
import requests
import logging

# # configurando os logs
# logging.basicConfig(
#   filename='app.log',  # Nome do arquivo onde os logs serão salvos
#   level=logging.INFO, # nivel minimo de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
#   format='%(asctime)s - %(levelname)s - %(message)s', # formato do log
#   datefmt='%Y-%m-%d %H:%M:%S' # formato da data e hora da ocorrencia do log
# )


# Criando um logger
logger = logging.getLogger('MeuLogger')
logger.setLevel(logging.DEBUG)

# Criando manipuladores
console_handler = logging.StreamHandler()  # Saída no console
file_handler = logging.FileHandler('app.log')  # Salva em arquivo

# Definindo nível para cada manipulador
console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

# Definindo formato do log
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Aplicando o formato nos handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Adicionando os handlers ao logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

class Scraper:
  def __init__(self):
    self.session = requests.Session() # sessão para otimizar as conexões de rede
    self.home_page = 'https://www.mercadolivre.com.br/' # pagina root do mercado livre
    self.categories = None
    self.headers = {
      'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
      'Connection': 'keep-alive',
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:136.0) Gecko/20100101 Firefox/136.0'
    }
    for _ in range(2): self.scrapeCategories()
  
  def scrapeCategories(self) -> list[str]:
    tree = self.getTree(self.home_page)
    if tree is None:
      logger.error(f'Arvore da home page esta vazia!')
      return None
    list_of_categories = tree.xpath('//ul[ @data-js="nav-categs-departments" ]/li//a//text()')
    list_of_categories.pop()
    if self.categories is None:
      self.categories = list_of_categories
    return list_of_categories

  def getTree(self, url: str): 
    '''
      obtem a arvore do html para fazer parsing
    '''
    try:
      response = self.session.get(url, headers=self.headers)
      if response.ok:
        logger.info(f'Tree da url: {url} - obtido!')
        return html.fromstring(response.text)
      else:
        logger.warning(f'Erro ao fazer a requisição ou obter a arvore da url: {url} - request status code: {response.status_code}')
    
    except Exception as e:
      logger.critical(f'Erro ao fazer requisição na url: {url} - Excessao: {e}')

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

  def getProductDescription(self, tree = None, url: str = None) -> list[str] | None:
    if url is not None and tree is None:
      tree = self.getTree(url)
      if tree is None:
        return None
      description = tree.xpath("//div[contains(@class, 'ui-pdp-description')]//p[contains(@class, 'ui-pdp-description__content')]//text()")
      return description
    
    description = tree.xpath("//div[contains(@class, 'ui-pdp-description')]//p[contains(@class, 'ui-pdp-description__content')]//text()")
    return description

  def scrapeProduct(self, url: str) -> dict | None:
    '''
      Raspa o produto da url passada como parametro,
      valida se o nome, preço, avaliação e descrição
      foram coletador e retorna um dicionario com os dados
    '''
    tree = self.getTree(url)
    if tree is None:
      logger.critical(f'Tree da url: {url} - está vazia!')
      return None
    
    product_name = self.getProductName(tree)
    price = self.getPrice(tree)
    rating = self.getRating(tree)
    description = self.getProductDescription(tree)

    if not product_name:
      logger.debug(f'Nome do produto: {url} - esta vazio!')
      return None
    
    elif not price:
      logger.debug(f'Preço do produto: {url} - esta vazio!')
      return None
    
    elif not rating:
      logger.debug(f'A avaliação do produto: {url} - esta vazia!')
      return None
    
    elif not description:
      logger.debug(f'A descrição do produto: {url} - esta vazia!')
      return None
    
    logger.info(f'Dados do produto: {url} - obtidos!')
    return {
      'product_name': product_name,
      'price': price,
      'rating': rating,
      'description': description
    }

  def scrapeProducts(self, urls: list | tuple) -> list[dict] | None:
    products_data = [ self.scrapeProduct(url) for url in urls ]
    if products_data is None:
      logger.debug(f'Lista de dados de scrapeProductsList() esta vazia!')
      return None
    return products_data

  def scrapeProductsLinks(self, url: str) -> None:
    tree = self.getTree(url) # pagina onde vai ter os produtos
    if tree is None:
      return None
    
    products_links = tree.xpath("//div[ contains(@class, 'poly-card__content') ]//a[ starts-with(@href, 'https://produto.mercadolivre.com.br/') or starts-with(@href, 'https://www.mercadolivre.com.br/') ]/@href")
    if products_links is None:
      logger.critical(f'Lista de links dos produtos esta vazia! url: {url}')
      return None
    return products_links
