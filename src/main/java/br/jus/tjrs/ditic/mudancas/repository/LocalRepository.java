package br.jus.tjrs.ditic.mudancas.repository;

import br.jus.tjrs.ditic.mudancas.model.Local;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface LocalRepository extends JpaRepository<Local, Long> {

    Optional<Local> findByNome(String nome);

    List<Local> findAllByOrderByNomeAsc();
}
