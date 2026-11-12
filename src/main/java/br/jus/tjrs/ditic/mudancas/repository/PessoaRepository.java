package br.jus.tjrs.ditic.mudancas.repository;

import br.jus.tjrs.ditic.mudancas.model.Perfil;
import br.jus.tjrs.ditic.mudancas.model.Pessoa;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;
import java.util.Optional;

public interface PessoaRepository extends JpaRepository<Pessoa, Long> {

    Optional<Pessoa> findByLogin(String login);

    boolean existsByLogin(String login);

    long countByPerfilAndAtivoTrue(Perfil perfil);

    boolean existsByPerfil(Perfil perfil);

    List<Pessoa> findAllByOrderByNomeAsc();
}
