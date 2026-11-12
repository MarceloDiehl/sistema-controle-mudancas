package br.jus.tjrs.ditic.mudancas.service;

import br.jus.tjrs.ditic.mudancas.model.Demanda;
import br.jus.tjrs.ditic.mudancas.model.DemandaExcluida;
import br.jus.tjrs.ditic.mudancas.model.Situacao;
import br.jus.tjrs.ditic.mudancas.repository.DemandaExcluidaRepository;
import br.jus.tjrs.ditic.mudancas.repository.DemandaRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.EnumSet;
import java.util.List;

/**
 * Tarefas do servidor: a mudança automática de status pelas datas e a remoção definitiva da lixeira depois de
 * 30 dias. Rodam ao iniciar e a cada hora (a primeira depois da meia-noite já pega o dia novo).
 */
@Service
public class AutomacaoService {

    public static final int DIAS_LIXEIRA = 30;
    private static final Logger LOG = LoggerFactory.getLogger(AutomacaoService.class);

    private final DemandaRepository demandas;
    private final DemandaExcluidaRepository excluidas;
    private final FluxoDemanda fluxo;

    public AutomacaoService(DemandaRepository demandas, DemandaExcluidaRepository excluidas, FluxoDemanda fluxo) {
        this.demandas = demandas;
        this.excluidas = excluidas;
        this.fluxo = fluxo;
    }

    // cada ponto de entrada abre a própria transação (a chamada interna não passaria pelo proxy do Spring)
    @EventListener(ApplicationReadyEvent.class)
    @Transactional
    public void aoIniciar() { executar(); }

    @Scheduled(cron = "0 1 * * * *", zone = "America/Sao_Paulo")
    @Transactional
    public void deHoraEmHora() { executar(); }

    @Transactional
    public synchronized void executar() {
        int status = 0;
        for (Demanda d : demandas.paraAutomacao(EnumSet.of(Situacao.NOVA, Situacao.ACIONADA, Situacao.EM_ATENDIMENTO))) {
            if (fluxo.automatizar(d)) status++;
        }
        int removidas = limparLixeira();
        if (status + removidas > 0) LOG.info("Automação: {} demanda(s) com status alterado, {} removida(s) da lixeira.", status, removidas);
    }

    private int limparLixeira() {
        List<Demanda> vencidas = demandas.lixeiraVencida(fluxo.agora().minusDays(DIAS_LIXEIRA));
        for (Demanda d : vencidas) {
            DemandaExcluida reg = new DemandaExcluida();
            reg.setDemandaId(d.getId());
            reg.setSei(d.getSei());
            reg.setLocalTexto(d.getLocalTexto());
            reg.setSituacao(d.getSituacao().name());
            reg.setExcluidaEm(fluxo.agora());
            reg.setTexto("Demanda removida definitivamente da lixeira (" + DIAS_LIXEIRA + " dias sem restauração).");
            excluidas.save(reg);
            demandas.delete(d);
        }
        return vencidas.size();
    }
}
