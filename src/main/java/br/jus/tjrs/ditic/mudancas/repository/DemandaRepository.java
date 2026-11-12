package br.jus.tjrs.ditic.mudancas.repository;

import br.jus.tjrs.ditic.mudancas.model.Demanda;
import br.jus.tjrs.ditic.mudancas.model.Situacao;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.Collection;
import java.util.List;

public interface DemandaRepository extends JpaRepository<Demanda, Long> {

    /** Demandas fora da lixeira, com os subtickets (a lista principal). */
    @Query("""
            select distinct d from Demanda d left join fetch d.local
            left join fetch d.subtickets s left join fetch s.empresa left join fetch s.servico
            where d.excluidaEm is null""")
    List<Demanda> listarComSubtickets();

    @Query("""
            select distinct d from Demanda d left join fetch d.local
            left join fetch d.subtickets s left join fetch s.empresa left join fetch s.servico
            where d.excluidaEm is not null""")
    List<Demanda> listarLixeira();

    /** Quantos registros de histórico tem cada demanda: [id, quantidade]. */
    @Query("select h.demanda.id, count(h) from Historico h group by h.demanda.id")
    List<Object[]> contarHistorico();

    /** Candidatas à mudança automática de status pelas datas. */
    @Query("select d from Demanda d where d.excluidaEm is null and d.dataInicio is not null and d.situacao in :situacoes")
    List<Demanda> paraAutomacao(@Param("situacoes") Collection<Situacao> situacoes);

    @Query("select d from Demanda d where d.excluidaEm is not null and d.excluidaEm <= :limite")
    List<Demanda> lixeiraVencida(@Param("limite") LocalDateTime limite);

    /** Outra demanda (em aberto, encerrada ou na lixeira) que já usa o número como ticket principal ou subticket. */
    @Query("""
            select d from Demanda d where d.id <> :id and (d.ticketPrincipal = :numero
              or exists (select 1 from Subticket s where s.demanda = d and s.numero = :numero))
            order by d.id""")
    List<Demanda> comTicket(@Param("numero") String numero, @Param("id") Long id);

    List<Demanda> findBySeiAndIdNotOrderById(String sei, Long id);

    /** Outra demanda (em aberto, encerrada ou na lixeira) que já tem o número como subticket. */
    @Query("select s.demanda from Subticket s where s.numero = :numero and s.demanda.id <> :id")
    List<Demanda> comSubticket(@Param("numero") String numero, @Param("id") Long id);

    @Query("""
            select d from Demanda d where d.excluidaEm is null and d.carga = br.jus.tjrs.ditic.mudancas.model.Carga.TECNICO
              and d.tecnico.id = :tecnicoId and d.situacao in :situacoes""")
    List<Demanda> comTecnico(@Param("tecnicoId") Long tecnicoId, @Param("situacoes") Collection<Situacao> situacoes);
}
