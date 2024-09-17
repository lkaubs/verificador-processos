import time
from model.processo import Processo
from info.data_de_hoje import HOJE
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


def geraHtmlFasesSTJDiario(driver):
    elementos = driver.find_elements(By.CLASS_NAME, 'classDivFaseLinha')
    htmlFases1 = [elemento.get_attribute('outerHTML') for elemento in elementos]
    htmlFasesDoDia = ['\n   <div style="background-color:#f1e501;">\n' + fase + '\n   </div>\n' for fase in htmlFases1 if HOJE in fase]
    if len(htmlFasesDoDia) < 5:
        htmlFases = ('\n').join(htmlFasesDoDia) + ('\n').join(htmlFases1[len(htmlFasesDoDia):5])
    else:
        htmlFases = ('\n').join(htmlFasesDoDia)
    return htmlFases

def geraHtmlFasesSTJ(driver):
    elementos = driver.find_elements(By.CLASS_NAME, 'classDivFaseLinha')
    htmlFases1 = [elemento.get_attribute('outerHTML') for elemento in elementos]
    htmlFasesDoDia = ['\n   <div style="background-color:#f1e501;">\n' + fase + '\n   </div>\n' for fase in htmlFases1 if HOJE in fase]
    htmlFases = ('\n').join(htmlFasesDoDia)
    return htmlFases

def geraHtmlAbasSTJ(driver):
    elemento = driver.find_element(By.ID, 'idDivAbas')
    return elemento.get_attribute('outerHTML')
    
def geraHtmlDescricaoSTJ(driver):
    elemento = driver.find_element(By.ID, 'idDescricaoProcesso')
    return elemento.get_attribute('outerHTML')

def geraUltimoHtmlProcessoSTJ(numero_processo, htmlDescricao, htmlAbas, htmlFases):
    '''
    Gera o HTML do processo com as informações do STJ.
    O HTML gerado é uma réplica do site do STJ, mas com as informações 
    atualizadas e sem a necessidade de estar logado no site.
    
    :param numero_processo: Número do processo
    :param htmlDescricao: HTML da descrição do processo
    :param htmlAbas: HTML das abas do processo
    :param htmlFases: HTML das fases do processo
    :return: HTML emulado do processo das últimas 5 movimentações
    '''

    return '''
    <style type="text/css"> #idDescricaoProcesso {
                background-color: #414f55;
                background-repeat: no-repeat;
                border-top: 1px solid #FFFFFF;
                color: #FFFFFF;
                font-weight: bold;
                padding: 1em 0.25em 1em 0.25em;
                text-align: center;
            }
            body {
                font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
                font-size: 14px;
                line-height: 1.42857143;
                color: #333;
                background-color: #fff;
            }
            .classSpanFaseTexto {
                vertical-align: top;
                font-weight: bold;
                padding: 0 0 0 0.5em;
                display: inline-block;
                max-width: 70%;
                word-wrap: break-word;
            }
            .classDivFaseLinha {
                border-bottom: 1px solid;
                text-align: left;
                margin: 0.25em;
                padding: 0.25em 0;
            }

            .classDivConteudoPesquisaProcessual {
                background-color: #FFFFFF;
                clear: both;
                font-size: 1em;
                padding: 0.5em 0;
                text-align: justify;
                border: none;
                min-height: 4em;
                overflow: hidden;
            }
            #idDivAbas {
                display: block;
                background-color: #414f55;
                font-size: 1.1em;
                overflow: none;
                padding: 0 0 0 5px;
                border-style: none;
                margin-bottom: -1px;
            }
    </style>

    <ul style="background-color:#f1e501;">
        <li>''' + numero_processo + '''</li>
    </ul>
    <div>
        ''' + htmlDescricao + '''
    </div>
    <div>
        ''' + htmlAbas + '''
    </div>
    <div>
        ''' + htmlFases + '''
    </div>
    '''
# Inicializar o WebDriver (usando ChromeDriver como exemplo)
def geraHtmlDosProcessosJuntosDiarios():
    html = ''
    for processo in Processo.nao_separados():
        if bool(processo[6]):
            html += processo[3]
    
    return html

def geraHtmlDosProcessosJuntosNaoDiarios():
    html = ''
    for processo in Processo.nao_separados():
        if not bool(processo[6]):
            html += processo[3]
    return html

def atualizaHtmlDosProcessosNoBD():
    driver = webdriver.Chrome()
    lista_processos = Processo.list_by('numero_processo')
    
    for processo_bd in lista_processos:
        time.sleep(5)
        try:
            atualizaHtmldoProcessoNoBd(driver, processo_bd)
        except NoSuchElementException:
            for c in range(3):
                print(f"{c+1}ª consulta processual falhou.")
                print("Tentando novamente em 30 segundos")
                time.sleep(30)
                try:
                    atualizaHtmldoProcessoNoBd(driver, processo_bd)
                except NoSuchElementException:
                    continue
                break          
    driver.close()

def atualizaHtmldoProcessoNoBd(driver, processo_bd):
        instancia_processo = Processo.find_by_numero_processo(processo_bd[0])
        print(f'Verificando o processo {instancia_processo.numero_processo}')
        try:
            driver.get(instancia_processo.link)
        except Exception as err:
            print(err)

        match instancia_processo.tribunal:
            case Processo.STJ:
                ## procedimento se é STJ
                try: 
                    dataUltimaMovimentacao = driver.find_element(By.ID, 'idProcessoDetalhesBloco4').find_element(By.CLASS_NAME, 'classSpanDetalhesTexto').text.split()[0]
                    if instancia_processo.diario:
                        ## procedimento se é STJ e é diário
                        htmlDescricao = geraHtmlDescricaoSTJ(driver)
                        htmlAbas = geraHtmlAbasSTJ(driver)
                        htmlFases = geraHtmlFasesSTJDiario(driver)
                        
                        html = geraUltimoHtmlProcessoSTJ(instancia_processo.numero_processo, htmlDescricao, htmlAbas, htmlFases)

                        Processo.update_by_numero_processo(instancia_processo.numero_processo, {'ultimo_html': html, 'data_verificacao': HOJE})
                        Processo.save()

                    else:
                        ## procedimento se é STJ e não é diário
                        if dataUltimaMovimentacao == HOJE:
                            ## procedimento se teve movimentação
                            htmlDescricao = geraHtmlDescricaoSTJ(driver)
                            htmlAbas = geraHtmlAbasSTJ(driver)
                            htmlFases = geraHtmlFasesSTJ(driver)
                            
                            html = geraUltimoHtmlProcessoSTJ(instancia_processo.numero_processo, htmlDescricao, htmlAbas, htmlFases)

                            Processo.update_by_numero_processo(instancia_processo.numero_processo, {'ultimo_html': html, 'data_verificacao': HOJE})
                            Processo.save()

                        else:
                            ## procedimento se não teve movimentação
                            print("Não teve nenhuma movimentação.")
                            Processo.update_by_numero_processo(instancia_processo.numero_processo, {'data_verificacao': HOJE})
                            Processo.save()

                except NoSuchElementException as err:
                    raise err
            case Processo.STF:
                print("Sistema não implementado ainda")
