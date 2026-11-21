# -*- coding: utf-8 -*-
"""
Módulo M1 — cache de blocos (buffer cache).

Referência: Silberschatz, 9ª ed., 13.4.3 (Caching) e 12.6 (Efficiency and Performance) — pesquisa.

Implementem CacheLRU e CacheFIFO com a interface abaixo. O simulador de E/S chama:

    ler(bloco) -> bool
        True se o bloco está na cache (acerto). Num acerto, a LRU atualiza a recência;
        a FIFO não muda nada.
    inserir(bloco) -> list[int]
        Chamado depois de uma falta de leitura, quando o bloco chega do disco. Se a cache
        estiver cheia, expulsa uma vítima (LRU: a usada há mais tempo; FIFO: a que entrou
        primeiro). Devolve os blocos SUJOS expulsos, que o simulador vai gravar no disco.
    escrever(bloco) -> list[int]
        Escrita do usuário. Coloca (ou atualiza) o bloco na cache e devolve a lista de blocos
        que precisam ser gravados no disco AGORA:
          write-through: o próprio bloco (+ sujos expulsos, que não existem nesta política);
          write-back:    só os blocos sujos expulsos; o bloco escrito fica marcado como sujo.
        Uma escrita conta como acesso para a LRU.
    sincronizar() -> list[int]
        Gravação periódica (a cada INTERVALO_SYNC_MS): devolve todos os blocos sujos e os
        marca como limpos.
    sujos() -> int
        Quantos blocos estão sujos agora (usado para medir a perda numa queda de energia).

Política de escrita: 'write-through' ou 'write-back'.
"""

from collections import OrderedDict


class Cache:
    nome = "?"

    def __init__(self, capacidade, escrita="write-back"):
        if escrita not in ("write-through", "write-back"):
            raise ValueError("escrita deve ser 'write-through' ou 'write-back'")
        if capacidade < 0:
            raise ValueError("capacidade não pode ser negativa")
        self.capacidade = capacidade
        self.escrita = escrita
        self._blocos = OrderedDict()

    def ler(self, bloco):
        if bloco not in self._blocos:
            return False
        if self.nome == "LRU":
            self._blocos.move_to_end(bloco)
        return True

    def inserir(self, bloco):
        if bloco in self._blocos:
            if self.nome == "LRU":
                self._blocos.move_to_end(bloco)
            return []
        return self._inserir(bloco, False)

    def escrever(self, bloco):
        sujos = self._inserir(bloco, self.escrita == "write-back")
        return sujos + [bloco] if self.escrita == "write-through" else sujos

    def sincronizar(self):
        sujos = [bloco for bloco, sujo in self._blocos.items() if sujo]
        for bloco in sujos:
            self._blocos[bloco] = False
        return sujos

    def sujos(self):
        return sum(1 for sujo in self._blocos.values() if sujo)

    def _inserir(self, bloco, sujo):
        if bloco in self._blocos:
            self._blocos[bloco] = sujo or self._blocos[bloco]
            if self.nome == "LRU":
                self._blocos.move_to_end(bloco)
            return []
        if self.capacidade == 0:
            return []
        expulsos = []
        if len(self._blocos) == self.capacidade:
            vitima, dirty = self._blocos.popitem(last=False)
            if dirty:
                expulsos.append(vitima)
        self._blocos[bloco] = sujo
        return expulsos


class CacheLRU(Cache):
    nome = "LRU"

    def __init__(self, capacidade, escrita="write-back"):
        super().__init__(capacidade, escrita)


class CacheFIFO(Cache):
    nome = "FIFO"

    def __init__(self, capacidade, escrita="write-back"):
        super().__init__(capacidade, escrita)


CACHES = {"LRU": CacheLRU, "FIFO": CacheFIFO}


def criar_cache(nome, capacidade, escrita):
    try:
        return CACHES[nome](capacidade, escrita)
    except KeyError:
        raise ValueError("cache desconhecida: %s" % nome)
