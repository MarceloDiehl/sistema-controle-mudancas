package br.jus.tjrs.ditic.mudancas.model;

import java.util.Arrays;
import java.util.EnumSet;
import java.util.Set;

/** Situação da demanda. {@code id} é o nome usado pela tela; {@code rotulo}, o texto do histórico. */
public enum Situacao {
    NOVA("nova", "Nova"),
    ACIONADA("acionada", "Acionada"),
    EM_ATENDIMENTO("atendimento", "Em atendimento"),
    PARA_VALIDACAO("pendente", "Para validação"),
    CONCLUIDA("concluida", "Concluída"),
    CANCELADA("cancelada", "Cancelada");

    public static final Set<Situacao> ABERTAS = EnumSet.of(NOVA, ACIONADA, EM_ATENDIMENTO, PARA_VALIDACAO);
    /** O status anda sozinho pelas datas; os dados continuam editáveis. */
    public static final Set<Situacao> AUTOMATICAS = EnumSet.of(EM_ATENDIMENTO, PARA_VALIDACAO);

    private final String id;
    private final String rotulo;

    Situacao(String id, String rotulo) {
        this.id = id;
        this.rotulo = rotulo;
    }

    public String id() { return id; }

    public String rotulo() { return rotulo; }

    public boolean aberta() { return ABERTAS.contains(this); }

    public static Situacao doId(String id) {
        return Arrays.stream(values()).filter(s -> s.id.equals(id)).findFirst().orElse(null);
    }
}
