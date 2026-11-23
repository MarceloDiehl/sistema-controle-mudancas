package br.jus.tjrs.ditic.mudancas.dto;

import java.util.List;

/** Equipe, contas e solicitações de acesso. */
public final class EquipeDtos {

    private EquipeDtos() { }

    /** acesso: "aguardando" (primeiro acesso), "ativo" ou "desativado". */
    public record Pessoa(String id, String login, String nome, String curto, String ini, String cor, String perfil,
                         boolean ativo, String acesso, String ultimoAcesso) { }

    /** Toda conta nova é de técnico: o administrador é um só. */
    public record NovaPessoa(String nome, String login, String cor) { }

    public record Edicao(String nome, String cor) { }

    /** para: id do técnico ou "coordenador" (a carga do Administrador). Com desativar, a conta é excluída e as desmarcadas vão para o Administrador. */
    public record Transferencia(String para, List<Long> demandas, boolean desativar) { }

    /** A senha temporária aparece uma única vez, para o administrador entregar à pessoa. */
    public record SenhaTemporaria(Pessoa pessoa, String senha, String expiraEm) { }

    /** apagada: a conta saiu do banco; senão foi desativada e o nome segue no histórico. */
    public record Exclusao(String nome, boolean apagada) { }

    public record Solicitacao(Long id, String nome, String login, String pedidaEm) { }

    public record PedidoAcesso(String nome, String login) { }

    public record Aprovacao(String cor) { }

    public record Login(String usuario, String senha) { }

    public record TrocaSenha(String atual, String nova) { }

    public record Sessao(String id, String login, String nome, String perfil, boolean deveTrocarSenha) { }
}
