from model.processo import Processo

while True:
    resposta = input()
    if not resposta:
        break
    tipo = resposta.split()[0]
    num = resposta.split()[1]
    processo = Processo.new(resposta, f"https://processo.stj.jus.br/processo/pesquisa/?termo={tipo}+{num}&aplicacao=processos.ea&tipoPesquisa=tipoPesquisaGenerica&chkordem=DESC&chkMorto=MORTO",
                        ultimo_html="", data_verificacao="", tribunal="STJ", separado=1, diario=1)
    Processo.save()