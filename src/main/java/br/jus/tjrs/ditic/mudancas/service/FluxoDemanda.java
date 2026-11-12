package br.jus.tjrs.ditic.mudancas.service;

import br.jus.tjrs.ditic.mudancas.model.Carga;
import br.jus.tjrs.ditic.mudancas.model.Demanda;
import br.jus.tjrs.ditic.mudancas.model.Historico;
import br.jus.tjrs.ditic.mudancas.model.Perfil;
import br.jus.tjrs.ditic.mudancas.model.Pessoa;
import br.jus.tjrs.ditic.mudancas.model.Situacao;
import br.jus.tjrs.ditic.mudancas.model.TipoAviso;
import br.jus.tjrs.ditic.mudancas.model.TipoHistorico;
import br.jus.tjrs.ditic.mudancas.repository.PessoaRepository;
import org.springframework.stereotype.Component;

import java.time.Clock;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.temporal.ChronoUnit;

import static br.jus.tjrs.ditic.mudancas.service.Formatos.br;

/**
 * Peças comuns do fluxo da demanda: histórico, bolinha azul, troca de responsável e a mudança automática de status
 * pelas datas.
 */
@Component
public class FluxoDemanda {

    /** Na tela, a carga compartilhada dos coordenadores aparece com este id no campo Responsável. */
    public static final String COORDENADOR = "coordenador";
    /** Valor de aviso_para quando o aviso é para os coordenadores. */
    public static final String AVISO_COORDENADOR = "COORDENADOR";

    private final Clock relogio;
    private final PessoaRepository pessoas;

    public FluxoDemanda(Clock relogio, PessoaRepository pessoas) {
        this.relogio = relogio;
        this.pessoas = pessoas;
    }

    public LocalDate hoje() { return LocalDate.now(relogio); }

    public LocalDateTime agora() { return LocalDateTime.now(relogio).truncatedTo(ChronoUnit.SECONDS); }

    /** Responsável escolhido na tela: um técnico ativo ou os coordenadores. */
    public record Responsavel(Carga carga, Pessoa tecnico) {
        public static final Responsavel COORDENADORES = new Responsavel(Carga.COORDENADOR, null);
    }

    public Responsavel responsavel(String valor) {
        if (valor == null || valor.isBlank() || COORDENADOR.equals(valor)) return Responsavel.COORDENADORES;
        Pessoa p;
        try {
            p = pessoas.findById(Long.valueOf(valor)).orElse(null);
        } catch (NumberFormatException e) {
            p = null;
        }
        if (p == null || p.getPerfil() != Perfil.TECNICO) throw RegraException.invalido("Responsável não encontrado na Equipe.");
        if (!p.isAtivo()) throw RegraException.invalido(p.getNome() + " está desativado(a) e não pode receber demandas.");
        return new Responsavel(Carga.TECNICO, p);
    }

    public Responsavel responsavelAtual(Demanda d) { return new Responsavel(d.getCarga(), d.responsavelTecnico()); }

    public void registrar(Demanda d, TipoHistorico tipo, String texto, Pessoa autor) {
        Historico h = new Historico();
        h.setDemanda(d);
        h.setDataHora(agora());
        h.setAutor(autor);
        h.setTipo(tipo);
        h.setTexto(texto.length() > 500 ? texto.substring(0, 500) : texto);
        d.getHistorico().add(h);
        d.setAtualizadaEm(h.getDataHora());
    }

    /** Acende a bolinha azul para quem está com a demanda (a Concluída fica com o Setor e não tem aviso). */
    public void avisar(Demanda d, TipoAviso tipo) {
        String para = switch (d.getCarga()) {
            case TECNICO -> String.valueOf(d.getTecnico().getId());
            case COORDENADOR -> AVISO_COORDENADOR;
            case SETOR -> null;
        };
        d.setAvisoTipo(para == null ? null : tipo);
        d.setAvisoPara(para);
        d.setAvisoEm(para == null ? null : agora());
    }

    public void limparAviso(Demanda d) {
        d.setAvisoTipo(null);
        d.setAvisoPara(null);
        d.setAvisoEm(null);
    }

    public static String nome(Responsavel r) {
        return switch (r.carga()) {
            case TECNICO -> r.tecnico().getNome();
            case COORDENADOR -> "Coordenador";
            case SETOR -> "Setor";
        };
    }

    /** "atribuída ao Coordenador" ou "atribuída a Ana Souza". */
    public static String atribuidaA(Responsavel r) {
        return r.carga() == Carga.COORDENADOR ? "atribuída ao Coordenador" : "atribuída a " + nome(r);
    }

    /**
     * Passa a demanda para outro responsável e avisa quem recebe ("retornou" se já passou pelo técnico antes).
     * Com {@code motivo} diferente de null, registra a troca no histórico. Devolve false se nada mudou.
     */
    public boolean atribuir(Demanda d, Responsavel novo, Pessoa autor, String motivo) {
        Responsavel antes = responsavelAtual(d);
        boolean mesmo = antes.carga() == novo.carga()
                && (novo.carga() != Carga.TECNICO || antes.tecnico().getId().equals(novo.tecnico().getId()));
        if (mesmo) return false;
        if (novo.carga() == Carga.TECNICO) {
            d.setCarga(Carga.TECNICO);
            d.setTecnico(novo.tecnico());
        } else {
            // guarda o técnico que atendeu quando o atendimento já começou; antes disso a demanda volta sem técnico
            d.setCarga(Carga.COORDENADOR);
            if (antes.carga() == Carga.TECNICO) d.setTecnico(Situacao.AUTOMATICAS.contains(d.getSituacao()) ? antes.tecnico() : null);
        }
        boolean voltou = novo.carga() == Carga.TECNICO && d.getPassou().contains(novo.tecnico().getId());
        avisar(d, voltou ? TipoAviso.RETORNOU : TipoAviso.NOVA);
        if (novo.carga() == Carga.TECNICO) d.getPassou().add(novo.tecnico().getId());
        if (motivo != null) {
            registrar(d, TipoHistorico.RESPONSAVEL, "Responsável alterado: " + nome(antes) + " → " + nome(novo)
                    + (motivo.isEmpty() ? "" : " (" + motivo + ")") + ".", autor);
        }
        return true;
    }

    /** A data do acionamento nunca é depois da Data de Início. */
    public static LocalDate dataAcionamento(LocalDate data, Demanda d) {
        return d.getDataInicio() != null && data.isAfter(d.getDataInicio()) ? d.getDataInicio() : data;
    }

    /**
     * Mudança automática de status pelas datas, sem trocar o responsável. Devolve true se a demanda mudou.
     * Acionada → Em atendimento na Data de Início; Nova também, se já tem ticket principal e subticket.
     * Acionada ou Em atendimento → Para validação um dia depois da Data para Conclusão. Para validação nunca volta.
     */
    public boolean automatizar(Demanda d) {
        if (d.getExcluidaEm() != null || d.getDataInicio() == null) return false;
        LocalDate hoje = hoje();
        LocalDate inicio = d.getDataInicio();
        LocalDate fim = d.fimDoPeriodo();
        boolean mudou = false;
        // a Data de Início foi corrigida para antes do acionamento: o acionamento acompanha
        if (d.getAcionadaEm() != null && d.getAcionadaEm().isAfter(inicio)) {
            d.setAcionadaEm(inicio);
            mudou = true;
        }
        if (d.getSituacao() == Situacao.NOVA && !inicio.isAfter(hoje) && d.getTicketPrincipal() != null && !d.getSubtickets().isEmpty()) {
            d.setSituacao(Situacao.EM_ATENDIMENTO);
            // a data do acionamento é a do registro do ticket principal (quando as empresas foram acionadas)
            LocalDate ticket = d.getTicketEm() != null ? d.getTicketEm().toLocalDate() : hoje;
            d.setAcionadaEm(dataAcionamento(ticket, d));
            registrar(d, TipoHistorico.STATUS_AUTOMATICO, "Status alterado automaticamente: Nova → Em atendimento (tickets registrados e início do agendamento em " + br(inicio) + ").", null);
            avisar(d, TipoAviso.ATENDIMENTO);
            mudou = true;
        }
        if ((d.getSituacao() == Situacao.ACIONADA || d.getSituacao() == Situacao.EM_ATENDIMENTO) && fim.isBefore(hoje)) {
            String de = d.getSituacao().rotulo();
            d.setSituacao(Situacao.PARA_VALIDACAO);
            registrar(d, TipoHistorico.STATUS_AUTOMATICO, "Status alterado automaticamente: " + de + " → Para validação (o atendimento previsto terminou em " + br(fim) + ").", null);
            avisar(d, TipoAviso.PARA_VALIDACAO);
            mudou = true;
        } else if (d.getSituacao() == Situacao.ACIONADA && !inicio.isAfter(hoje)) {
            d.setSituacao(Situacao.EM_ATENDIMENTO);
            registrar(d, TipoHistorico.STATUS_AUTOMATICO, "Status alterado automaticamente: Acionada → Em atendimento (início do agendamento em " + br(inicio) + ").", null);
            avisar(d, TipoAviso.ATENDIMENTO);
            mudou = true;
        }
        if (mudou) d.setAtualizadaEm(agora());
        return mudou;
    }
}
