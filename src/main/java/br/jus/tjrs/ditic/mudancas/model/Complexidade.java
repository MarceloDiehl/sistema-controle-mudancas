package br.jus.tjrs.ditic.mudancas.model;

import java.util.Arrays;

/** Complexidade da demanda, escolhida na Nova Demanda (padrão Normal). {@code id} é o nome usado pela tela. */
public enum Complexidade {
    BAIXA("baixa", "Baixa"),
    NORMAL("normal", "Normal"),
    ALTA("alta", "Alta");

    private final String id;
    private final String rotulo;

    Complexidade(String id, String rotulo) {
        this.id = id;
        this.rotulo = rotulo;
    }

    public String id() { return id; }

    public String rotulo() { return rotulo; }

    public static Complexidade doId(String id) {
        return Arrays.stream(values()).filter(c -> c.id.equals(id)).findFirst().orElse(null);
    }
}
