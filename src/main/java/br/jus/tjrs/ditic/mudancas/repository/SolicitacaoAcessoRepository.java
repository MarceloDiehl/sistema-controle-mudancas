package br.jus.tjrs.ditic.mudancas.repository;

import br.jus.tjrs.ditic.mudancas.model.SituacaoSolicitacao;
import br.jus.tjrs.ditic.mudancas.model.SolicitacaoAcesso;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface SolicitacaoAcessoRepository extends JpaRepository<SolicitacaoAcesso, Long> {

    List<SolicitacaoAcesso> findBySituacaoOrderByPedidaEmAsc(SituacaoSolicitacao situacao);

    boolean existsByLoginAndSituacao(String login, SituacaoSolicitacao situacao);

    long countBySituacao(SituacaoSolicitacao situacao);
}
